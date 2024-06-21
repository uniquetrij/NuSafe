import itertools
import json

import google.generativeai as genai
import requests
from PIL import Image
from google.generativeai import GenerationConfig

import env
from ai.schemas import product_analysis_schema

__keys = itertools.cycle(env.GEMINI_KEYS)


def analyse_product(image_url: str, *items: str, **categorized_items: set[str] | tuple[str] | list[str]) -> dict[dict]:
    schema = schemas.product_analysis_schema(*items, **categorized_items)
    genai.configure(api_key=next(__keys))
    response = genai.GenerativeModel(env.GEMINI_FLASH).generate_content([
        env.GEMINI_PROMPT_ANALYZE_PRODUCT.format(json.dumps(schema, indent=2)),
        Image.open(requests.get(image_url, stream=True).raw)
    ], generation_config=GenerationConfig(
        temperature=0,
        top_k=64,
        top_p=0.95,
        max_output_tokens=4096,
        response_mime_type='application/json',
        response_schema=schema
    ))
    response.resolve()
    return json.loads(response.text)