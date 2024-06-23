import ast
import json

import env


def __process_args(
        *concerns: str, **categorized_concerns: set[str] | tuple[str] | list[str]
) -> dict:
    if concerns and categorized_concerns:
        categorized_concerns["others"] = concerns
    elif concerns:
        categorized_concerns = {"others": concerns}
    else:
        categorized_concerns = {}
    return categorized_concerns


def __process_config(d: dict[str, tuple[str]], **kwargs: str) -> dict:
    return {
        field: {
            "type": datatype,
            "description": description.format(**kwargs),
            **(dict(enum=enum) if enum else dict()),
        }
        for field, (datatype, description, enum) in d.items()
    }


def product_analysis_schema(
        *concerns: str, **categorized_concerns: set[str] | tuple[str] | list[str]
) -> dict:
    categorized_concerns = __process_args(*concerns, **categorized_concerns)

    schema: dict = {
        # "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "description": env.schemas.PRIMARY_INSTRUCTION,
        "properties": {
            "ocr": {
                "type": "string",
                "description": env.schemas.OCR_INSTRUCTION,
            },
        },
    }

    schema["properties"].update({
        "meta": {
            "type": "object",
            "description": env.schemas.META_INSTRUCTION,
            "properties": __process_config(env.schemas.META_INDICATORS),
        }
    })

    schema["properties"].update({
        "concerns": {
            "type": "object",
            "description": env.schemas.CONCERNS_INSTRUCTION,
            "properties": {
                group: {
                    "type": "object",
                    "description": env.schemas.CONCERN_GROUP_INSTRUCTION.format(group=group),
                    "properties": {
                        concern: {
                            "type": "object",
                            "description": env.schemas.CONCERN_ITEM_INSTRUCTION.format(concern=concern),
                            "properties": {
                                "constituents": {
                                    "type": "array",
                                    "description": env.schemas.CONSTITUENTS_INSTRUCTION.format(concern=concern),
                                    "items": {
                                        "type": "object",
                                        "description": env.schemas.CONSTITUENT_ITEM_INSTRUCTION.format(concern=concern),
                                        "properties": __process_config(
                                            env.schemas.CONSTITUENT_ITEM_INDICATORS, concern=concern
                                        ),
                                    },
                                },
                                **(
                                    __process_config(env.schemas.CONCERN_ITEM_INDICATORS, concern=concern)
                                ),
                            },
                        }
                        for concern in set(concerns)
                    },
                }
                for group, concerns in categorized_concerns.items()
            },
        },
    })

    return schema


if __name__ == "__main__":

    # print(json.dumps(product_analysis_schema("cholesterol", "diabetes"), indent=2, ensure_ascii=False))
    # print(json.dumps(product_analysis_schema(), indent=2, ensure_ascii=False))
    d = '''{
        "type": "object",
        "description": "You are a smart professional nutritionist to assist users and ensure that "
                       "they are consuming the correct grocery / cosmetic / pharmaceutical products, "
                       "safe for their health, given their health condition, if any.",
        "properties": {
            "introduction": {
                "type": "string",
                "description": "Introduce yourself in not more than 25 words.",
            }
        }
    }'''
    ast.literal_eval(d)
