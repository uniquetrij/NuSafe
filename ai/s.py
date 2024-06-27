import json

import env


def __format_schema_properties(d: dict[str, tuple[str]], **kwargs: str) -> dict:
    return {
        field: {
            "type": datatype if datatype not in ['date-time'] else 'string',
            "description": description.format(**kwargs),
            **(dict(enum=enum) if enum else dict()),
            **(dict(format=datatype) if datatype in ['date-time'] else dict()),
        }
        for field, (datatype, description, enum) in d.items()
    }


def instruction_schema(**members: dict[str, dict[str, ...]]):
    return {
        "type": "object",
        "description": env.schema.PRIMARY_INSTRUCTION,
        "properties": {
            **__ocr(),
            **__meta(),
            **__health(),
            **__product(members)
        }
    }


def __health():
    return {
        "health": {
            "type": "object",
            "description": env.schema.HEALTH_INSTRUCTION,
            "properties": {
                "report": {
                    "type": "object",
                    "description": env.schema.HEALTH_REPORT_INSTRUCTION,
                    "properties": {
                        **__format_schema_properties(env.schema.HEALTH_REPORT_INDICATORS)
                    }
                },
                "demography": {
                    "type": "object",
                    "description": env.schema.HEALTH_DEMOGRAPTHY_INSTRUCTION,
                    "properties": {
                        **__format_schema_properties(env.schema.HEALTH_DEMOGRAPTHY_INDICATORS)
                    }
                },
                "vitals": {
                    "type": "object",
                    "description": env.schema.HEALTH_VITALS_INSTRUCTION,
                    "properties": {
                        **__format_schema_properties(env.schema.HEALTH_VITALS_INDICATORS)
                    }
                },
                "issues": {
                    "type": "array",
                    "description": env.schema.HEALTH_CONCERNS_INSTRUCTION,
                    "items": {
                        "type": "object",
                        "description": env.schema.HEALTH_CONCERNS_ITEMS_INSTRUCTION,
                        "properties": {
                            **__format_schema_properties(env.schema.HEALTH_CONCERNS_ITEMS_INDICATORS),
                            "precautions": {
                                "type": "array",
                                "description": env.schema.HEALTH_CONCERNS_ITEMS_PRECAUTIONS_INSTRUCTION,
                                "items": {
                                    "type": "object",
                                    "description": env.schema.HEALTH_CONCERNS_ITEMS_PRECAUTIONS_INDICATORS_INSTRUCTION,
                                    "properties": {
                                        **__format_schema_properties(
                                            env.schema.HEALTH_CONCERNS_INGREDIENT_INDICATORS)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


def __product(members):
    return {
        "product": {
            "type": "object",
            "description": env.schema.PRODUCT_INSTRUCTION,
            "properties": {
                "specific": {
                    "type": "object",
                    "description": env.schema.PRODUCT_SPECIFIC_INSTRUCTION,
                    "properties": {
                        member: {
                            "type": "object",
                            "description": env.schema.PRODUCT_SPECIFIC_MEMBER_INSTRUCTION.format(member=member,
                                                                                                 vitals=vitals,
                                                                                                 concerns=concerns),
                            "properties": {
                                concern: {
                                    "type": "object",
                                    "description": env.schema.PRODUCT_SPECIFIC_MEMBER_CONCERN_INSTRUCTION.format(
                                        member=member, concern=concern),
                                    "properties": {
                                        "constituents": {
                                            "type": "array",
                                            "description": env.schema.CONSTITUENTS_INSTRUCTION.format(
                                                concern=concern),
                                            "items": {
                                                "type": "object",
                                                "description": env.schema.CONSTITUENTS_ITEM_INSTRUCTION.format(
                                                    concern=concern),
                                                "properties": __format_schema_properties(
                                                    env.schema.CONSTITUENTS_ITEM_INDICATORS,
                                                    member=member,
                                                    concern=concern
                                                )
                                            }
                                        },
                                        **(
                                            __format_schema_properties(
                                                env.schema.PRODUCT_ITEM_INDICATORS,
                                                concern=concern, member=member)
                                        )
                                    }
                                } for concern, level in concerns.items()
                            }
                        } for member, (v, c) in members.items() if
                        (vitals := members[member][v]) | (concerns := members[member][c])
                    }
                },
                "generic": {
                    "type": "object",
                    "description": env.schema.PRODUCT_GENERIC_INSTRUCTION,
                    "properties": {
                        'allergens': {
                            "type": "array",
                            "description": env.schema.PRODUCT_ALLERGENS_INSTRUCTION,
                            "items": {
                                "type": "object",
                                "description": env.schema.PRODUCT_ALLERGENS_ITEM_INSTRUCTION,
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "proportion": {
                                        "type": "number"
                                    },
                                    "justification": {
                                        "type": "string"
                                    }
                                }
                            }
                        },
                        'acutes': {
                            "type": "array",
                            "description": env.schema.PRODUCT_ACUTES_INSTRUCTION,
                            "items": {
                                "type": "object",
                                "description": env.schema.PRODUCT_ACUTES_ITEM_INSTRUCTION,
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "proportion": {
                                        "type": "number"
                                    },
                                    "justification": {
                                        "type": "string"
                                    }
                                }
                            }
                        },
                        'chronics': {
                            "type": "array",
                            "description": env.schema.PRODUCT_CHRONICS_INSTRUCTION,
                            "items": {
                                "type": "object",
                                "description": env.schema.PRODUCT_CHRONICS_ITEM_INSTRUCTION,
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "proportion": {
                                        "type": "number"
                                    },
                                    "justification": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                },
                "verdict": {
                    "type": "string",
                    "description": "Your final verdict whether I should purchase this product or not considering the health issues and concerns or my family members."
                },
            }
        }
    }


def __meta():
    return {
        "meta": {
            "type": "object",
            "description": env.schema.META_INSTRUCTION,
            "properties": __format_schema_properties(env.schema.META_INDICATORS),
        }
    }


def __ocr():
    return {
        "ocr": {
            "type": "string",
            "description": env.schema.OCR_INSTRUCTION,
        }
    }


if __name__ == "__main__":
    print(json.dumps(instruction_schema(
        mother={
            "vitals": {
                "age": "65",
                "sex": "female"
            },
            "concerns": {
                "diabetes": 0.5,
                "cholesterol": 0.9,
            }
        },
    ), indent=4))
