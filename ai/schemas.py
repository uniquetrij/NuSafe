import json

import env


def __process_args(*concerns: str, **categorized_concerns: set[str] | tuple[str] | list[str]) -> dict:
    if concerns and categorized_concerns:
        categorized_concerns["others"] = concerns
    elif concerns:
        categorized_concerns = {"others": concerns}
    elif categorized_concerns:
        pass
    else:
        categorized_concerns = {}
    if 'allergens' in categorized_concerns.keys():
        raise KeyError
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


def product_analysis_schema(*concerns: str, **categorized_concerns: set[str] | tuple[str] | list[str]) -> dict:
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

    # meta properties
    schema["properties"].update({
        "meta": {
            "type": "object",
            "description": env.schemas.META_INSTRUCTION,
            "properties": __process_config(env.schemas.META_INDICATORS),
        }
    })

    # concern properties - allergens
    schema["properties"].update({
        "concerns": {
            "type": "object",
            "description": env.schemas.CONCERNS_INSTRUCTION,
            "properties": {
                'allergens': {
                    "type": "array",
                    "description": env.schemas.CONCERNS_ALLERGENS_INSTRUCTION,
                    "items": {
                        "type": "string",
                        "description": env.schemas.CONCERNS_ALLERGENS_ITEM_INSTRUCTION
                    }
                }
            },
        },
    })

    # concern properties - customs
    schema["properties"]["concerns"]["properties"].update({
        group: {
            "type": "object",
            "description": env.schemas.CONCERNS_GROUP_INSTRUCTION.format(
                group=group),
            "properties": {
                concern: {
                    "type": "object",
                    "description": env.schemas.CONCERNS_ITEM_INSTRUCTION.format(
                        concern=concern),
                    "properties": {
                        "constituents": {
                            "type": "array",
                            "description": env.schemas.CONSTITUENTS_INSTRUCTION.format(
                                concern=concern),
                            "items": {
                                "type": "object",
                                "description": env.schemas.CONSTITUENTS_ITEM_INSTRUCTION.format(
                                    concern=concern),
                                "properties": __process_config(
                                    env.schemas.CONSTITUENTS_ITEM_INDICATORS,
                                    concern=concern
                                ),
                            },
                        },
                        **(
                            __process_config(
                                env.schemas.CONCERNS_ITEM_INDICATORS,
                                concern=concern)
                        ),
                    },
                }
                for concern in set(concerns)
            },
        }
        for group, concerns in categorized_concerns.items()
    })

    # health properties
    schema["properties"].update({
        "health": {
            "type": "object",
            "description": env.schemas.HEALTH_INSTRUCTION,
            "properties": {
                "concerns": {
                    "type": "array",
                    "description": env.schemas.HEALTH_CONCERNS_INSTRUCTION,
                    "items": {
                        "type": "object",
                        "description": env.schemas.HEALTH_CONCERNS_ITEMS_INSTRUCTION,
                        "properties": {
                            "term": {
                                "type": "string",
                                "description": env.schemas.HEALTH_CONCERNS_ITEMS_TERM_INSTRUCTION
                            },
                            "name": {
                                "type": "string",
                                "description": env.schemas.HEALTH_CONCERNS_ITEMS_NAME_INSTRUCTION
                            },
                            "analysis": {
                                "type": "string",
                                "description": env.schemas.HEALTH_CONCERNS_ITEMS_ANALYSIS_INSTRUCTION
                            },
                            "prevention": {
                                "type": "string",
                                "description": env.schemas.HEALTH_CONCERNS_ITEMS_PREVENTION_INSTRUCTION,
                            },
                            "precautions": {
                                "type": "array",
                                "description": env.schemas.HEALTH_CONCERNS_ITEMS_PRECAUTIONS_INSTRUCTION,
                                "items": {
                                    "type": "object",
                                    "description": env.schemas.HEALTH_CONCERNS_ITEMS_PRECAUTIONS_INDICATORS_INSTRUCTION,
                                    "properties": {
                                        **__process_config(env.schemas.HEALTH_CONCERNS_INGREDIENT_INDICATORS)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })

    return schema


if __name__ == "__main__":
    # print(type(product_analysis_schema(optionals_1=env.schemas.CHRONIC)))
    print(json.dumps(product_analysis_schema(optionals_1=env.schemas.CHRONIC, optionals_2=env.schemas.ACUTE), indent=2,
                     ensure_ascii=False))
