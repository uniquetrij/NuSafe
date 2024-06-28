import base64
import itertools
import json
import logging
import os
import random
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import google.generativeai as genai
import requests
from PIL import Image
from google.generativeai import GenerationConfig

import env

_log = logging.getLogger(__name__)

__keys = env.GEMINI_KEYS
random.shuffle(__keys)
__keys = itertools.cycle(__keys)


def __sanitise_json(json_str, schema=None):
    for i in range(5):
        try:
            return json.loads(json_str)
        except json.decoder.JSONDecodeError as e:
            match e.msg:
                case 'Extra data':
                    json_str = json_str[:-1].strip()
                case "Expecting ',' delimiter":
                    json_str = (json_str + '}').strip()
    raise


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
            temperature=0,
            top_k=64,
            top_p=0,
            response_mime_type='application/json',
            # response_schema=schema,
        ))
    response.resolve()
    _log.debug(response.text)

    return __sanitise_json(response.text, schema)


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
