import base64
import itertools
import json
import logging
import os
import random
import re
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import google.generativeai as genai
import requests
from PIL import Image
from google.generativeai import GenerationConfig
from openai.lib.azure import AzureOpenAI

import env

_log = logging.getLogger(__name__)

__keys = env.GEMINI_KEYS
random.shuffle(__keys)
__keys = itertools.cycle(__keys)


def __fix_json(json_str, schema):
    balance = 0
    for i in range(len(json_str)):
        if json_str[i] == '{':
            balance += 1
        if json_str[i] == '}':
            balance -= 1
            if balance == 0:
                return json_str[:i] + '}'
    if balance > 0:
        return json_str + '}' * balance


def __sanitise_schema(schema):
    keys_to_remove = ["minimum", "maximum", "enum", "multipleOf", "required", "format"]

    if isinstance(schema, dict):
        return {k: __sanitise_schema(v) for k, v in schema.items() if k not in keys_to_remove}
    elif isinstance(schema, list):
        return [__sanitise_schema(item) for item in schema]
    else:
        return schema


def gemini(schema: dict, image: str | Image.Image) -> dict:
    prompt = f'Follow JSON schema. <JSONSchema>{json.dumps(schema)}</JSONSchema>'

    if isinstance(image, str):
        if __is_path(image):
            image = __path_to_image(image)
        elif __is_url(image):
            image = __url_to_image(image)
        elif __is_base64(image):
            image = __base64_to_image(image)

    genai.configure(api_key=next(__keys))

    response = genai.GenerativeModel(env.GEMINI_PRO).generate_content(
        [prompt, image],
        generation_config=GenerationConfig(
            temperature=0.25,
            top_k=64,
            top_p=0.95,
            response_mime_type='application/json',
            # response_schema=__sanitise_schema(schema),
        ))
    response.resolve()
    _log.debug(response.text)
    text = re.sub(r'\\([^"\\/bfnrt])', r'\\\\\1', response.text)
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError:
        return json.loads(__fix_json(text, schema))


def __is_path(string: str):
    return os.path.isfile(string) or os.path.isdir(string)


def __is_url(string: str):
    parsed = urlparse(string)
    return parsed.scheme and parsed.netloc


def __is_base64(string: str):
    try:
        # Remove base64 header if present
        if "base64," in string:
            string = string.split("base64,")[1]
        # Check if string can be decoded
        base64.b64decode(string, validate=True)
        return True
    except Exception:
        return False


def __path_to_image(path_string: str) -> Optional[Image.Image]:
    return Image.open(path_string)


def __base64_to_image(base64_string: str) -> Optional[Image.Image]:
    # noinspection PyUnresolvedReferences
    try:
        # Remove base64 header if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        # Decode the base64 string
        image_data = base64.b64decode(base64_string)

        # Create a BytesIO object from the byte data
        image_bytes = BytesIO(image_data)

        # Open the image using Pillow
        image = Image.open(image_bytes)

        return image
    except (base64.binascii.Error, IOError) as e:
        _log.debug(f"Error decoding the base64 string or processing the image: {e}")
        return None


def __url_to_image(url_string: str) -> Optional[Image.Image]:
    try:
        response = requests.get(url_string, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        image = Image.open(BytesIO(response.content))
        return image
    except requests.exceptions.RequestException as e:
        _log.debug(f"Error fetching the image from URL: {e}")
        return None
    except Exception as e:
        _log.debug(f"Error processing the image: {e}")
        return None


def openai(schema: dict, image: str | Image.Image) -> dict:
    prompt = f'Follow JSON schema. <JSONSchema>{json.dumps(schema)}</JSONSchema>'

    client = AzureOpenAI(
        azure_endpoint=env.OPENAI_URL,
        api_key=env.OPENAI_KEYS[0],
        api_version=env.OPENAI_VERSION
    )

    response = client.chat.completions.create(
        model=env.OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image,
                        },
                    },
                ],
            }
        ],
        seed=5549,
        temperature=0.8,
        max_tokens=4096,
        top_p=0.95,
        response_format={"type": "json_object"}
    )
    _log.debug(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)
