import json

from langcodes import Language

array = "array"
boolean = "boolean"
description = "description"
enum = "enum"
format = "format"
items = "items"
maximum = "maximum"
minimum = "minimum"
multipleOf = "multipleOf"
number = "number"
object = "object"
properties = "properties"
required = "required"
string = "string"
true = "true"
type = "type"
date = "date"
integer = "integer"


def instruction_schema(locale: str | None = None, **members: dict[str, dict[str, ...]]):
    return {
        type: object,
        properties: {
            **__ocr(locale),

            **__meta(),

            **__medical(),

            **__retail(locale, members),

            # **__feedback(),
        },
    }


def __localize(source, target, locale):
    return {
        target: {
            type: string,
            description: f"As an expert linguist and translator, rewrite `{source}` in {Language.get(locale).display_name(locale)} language."
        },
    } if locale else {}


def __ocr(locale):
    return {
        "ocr": {
            type: object,
            properties: {
                "content": {
                    type: string,
                    description: "Complete OCR maintaining semantic relationship.",
                },
                "languages": {
                    type: array,
                    description: "Languages used in `ocr.content`.",
                    items: {
                        type: string,
                        description: "Format: 2 letters ISO 639-1."
                    },
                },
                **__localize('ocr.contents', f'content_l10n', locale)
            },
        },
    }


def __meta():
    return {
        "meta": {
            type: object,
            properties: {
                "description": {
                    type: string,
                    description: "Content description of image.",
                    enum: ["medical", "grocery", "cosmetic", "pharmaceutical"]
                },
                "legibility": {
                    type: number,
                    minimum: 0,
                    maximum: 1,
                    multipleOf: 0.01,
                    description: "Content readability from image."
                },
            }
        }
    }


def __medical():
    return {
        "medical": {
            type: object,
            description: "This section is enabled only when `meta.description`==`medical`; null otherwise.",
            properties: {
                "date": {
                    type: string,
                    format: date,
                    description: "Date stated in `ocr.content`; YYYY/MM/DD",
                },
                "patient": {
                    type: object,
                    properties: {
                        "name": {
                            type: string,
                            description: "Patient's name in `ocr.content`",
                        },
                        "age": {
                            type: number,
                            description: "Patient's age in `ocr.content`",
                        },
                        "sex": {
                            type: string,
                            description: "Patient's sex in `ocr.content`",
                            enum: ["male", "female", "others"]
                        },
                        "height": {
                            type: string,
                            description: "Patient's height in `ocr.content`",
                        },
                        "wight": {
                            type: string,
                            description: "Patient's wight in `ocr.content`",
                        },
                        "blood": {
                            type: string,
                            description: "Patient's blood group in `ocr.content`",
                            enum: ["A+", "B+", "AB+", "O+", "A-", "B-", "AB-", "O-"],
                        },
                        "pressure": {
                            type: string,
                            description: "Patient's blood pressure in `ocr.content`",
                        },
                    }
                },
                "issues": {
                    type: array,
                    description: "List of medical issues mentioned in `ocr.content`",
                    items: {
                        type: object,
                        properties: {
                            "i": {
                                type: integer,
                                description: "ARRAY_INDEX"
                            },
                            "term": {
                                type: string,
                                description: "The common term of the health issue as stated in `ocr.content`.",
                            },
                            "terminology": {
                                type: string,
                                description: "The medical terminology for `medical.issues[i].term`.",
                            },
                        },
                    },
                },
                "precautions": {
                    type: array,
                    required: true,
                    description: "Now you are a medical professional with an advanced degree in medical sciences. "
                                 "Based on your prior experience, wisdom and medical knowledge list all food "
                                 "ingredients that may aggravate `medical.issues[:].terminology` and should be "
                                 "avoided.",
                    items: {
                        type: object,
                        description: "A nutrient or ingredient that the patient should avoid (unique name only), "
                                     "along with its criticality.",
                        properties: {
                            "name": {
                                type: string
                            },
                            "type": {
                                type: string,
                            },
                            "criticality": {
                                type: number,
                                minimum: 0,
                                maximum: 1,
                                multipleOf: 0.001,
                                description: "How severely it may impact the patient's health."
                            }
                        }
                    }
                }
            },
        },
    }


def __retail(locale, members):
    return {
        "retail": {
            type: object,
            description: "This section is enabled only when `meta.description`!=`medical`; null otherwise.",
            properties: {
                "type": {
                    type: string,
                    enum: ["grocery", "cosmetic", "pharmaceutical"]
                },
                "generic": {
                    type: object,
                    description: "As a professional nutritionist and dietitian, prepare the generic disease profile "
                                 "of this product, either explicit from its nutrients and/or ingredients, or implicit "
                                 "based on your prior wisdom and medical knowledge.",
                    properties: {
                        "allergens": {
                            type: array,
                            items: {
                                type: object,
                                properties: {
                                    "name": {
                                        type: string
                                    },
                                    "proportion": {
                                        type: number
                                    },
                                    "reason": {
                                        type: string,
                                    }
                                }
                            }
                        },
                        "chronic": {
                            type: array,
                            description: "Chronic diseases that may be aggravated by the nutrients "
                                         "and/or ingredients present this product.",
                            items: {
                                type: array,
                                items: {
                                    type: object,
                                    properties: {
                                        "name": {
                                            type: string
                                        },
                                        "proportion": {
                                            type: number
                                        },
                                        "reason": {
                                            type: string,
                                        }
                                    }
                                }
                            }
                        },
                        "acute": {
                            type: array,
                            description: "Acute diseases that may be aggravated by the nutrients "
                                         "and/or ingredients present this product.",
                            items: {
                                type: array,
                                items: {
                                    type: object,
                                    properties: {
                                        "name": {
                                            type: string
                                        },
                                        "proportion": {
                                            type: number
                                        },
                                        "reason": {
                                            type: string,
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "specific": {
                    type: object,
                    description: "As a professional nutritionist and dietitian, help me decide whether this product "
                                 "is suitable for my family based on my family members' pre-existing health conditions "
                                 "and your prior wisdom and medical knowledge.",
                    properties: {
                        member: {
                            type: object,
                            description: f"{member}'s vital signs are {vitals}.",
                            properties: {
                                concern: {
                                    type: object,
                                    description: f"{member} has {concern}.",
                                    properties: {
                                        "constituents": {
                                            type: array,
                                            items: {
                                                type: object,
                                                properties: {
                                                    "name": {
                                                        type: string
                                                    },
                                                    "proportion": {
                                                        type: number
                                                    },
                                                    "criticality": {
                                                        type: number
                                                    }
                                                }
                                            }
                                        },
                                        **dict({
                                            "risk": {
                                                type: number
                                            },
                                            "justification": {
                                                type: string
                                            }
                                        })
                                    }
                                } for concern, level in concerns.items()
                            }
                        } for member, (v, c) in members.items() if
                        (vitals := members[member][v]) | (concerns := members[member][c])
                    }
                },
                "verdict": {
                    type: string,
                    description: "Your final verdict whether I should purchase this product or not considering "
                                 "the health issues and concerns or my family members."
                },
                **__localize('retail.verdict', f'verdict_l10n', locale)
            }
        },
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
    members = dict(

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
        father={
            "vitals": {
                "age": "70",
                "sex": "male"
            },
            "concerns": {
                "hypertension": 1,
            }
        },
        wife={
            "vitals": {
                "age": "25",
                "sex": "female"
            },
            "concerns": {
                "pregnant": 1,
            }
        },
    )
    print(json.dumps(instruction_schema(**members), indent=4))
