import json

type = "type"
description = "description"
properties = "properties"
object = "object"
string = "string"
number = "number"
array = "array"
enum = "enum"
items = "items"
required = "required"
true = "true"
minimum = "minimum"
maximum = "maximum"
multipleOf = "multipleOf"


def instruction_schema(locale: str = 'hi', **members: dict[str, dict[str, ...]]):
    return {
        type: object,
        properties: {
            **__ocr(locale),
            **__meta(),

            "medical": {
                type: object,
                description: "`medical` section enabled when `meta.content`==`medical`; null otherwise.",
                properties: {
                    "name": {
                        type: string
                    }
                }
            },

            "product": {
                type: object,
                description: "`product` section enabled when `meta.content`!=`medical`; null otherwise.",
                properties: {
                    "name": {
                        type: string
                    }
                }
            },

            **__feedback(),
        },
    }


def __localize(_ln_):
    return {
        properties: {
            "--": {
                type: string,
                required: true,
                description: "In original language. Replace key `--` with language name."
            },
            _ln_: {
                type: string,
                required: true,
                description: f"Translate from value of key `--` to {_ln_}."
            },
        },
    }


def __ocr(locale):
    return {
        "ocr": {
            type: array,
            required: true,
            items: {
                type: object,
                required: true,
                description: "Complete OCR; split page-wise.",
                **__localize(locale),
            },
        },
    }


def __meta():
    return {
        "meta": {
            type: object,
            properties: {
                "content": {
                    type: string,
                    enum: ["medical", "grocery", "cosmetic", "pharmaceutical", "null"]
                },
                "legibility": {
                    type: number,
                    minimum: 0,
                    maximum: 1,
                    multipleOf: 0.01,
                    description: "How easy it was to read from the image."
                }
            }
        }
    }


def __feedback():
    return {
        "_feedback": {
            type: string,
            required: true,
            description: "Were these instructions hard for you? Elaborate where you faced difficulty.",
        }
    }


if __name__ == "__main__":
    print(json.dumps(instruction_schema(), indent=4))
