import json

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


def instruction_schema(locale: str = 'hi', **members: dict[str, dict[str, ...]]):
    return {
        type: object,
        properties: {
            **__ocr(),

            **__meta(),

            **__medical(),

            #
            # **__retail(),
            #
            **__feedback(),
        },
    }


def __localize(locale):
    return {
        properties: {
            "<language-code>": {
                type: string,
                required: true,
                description: "In original language. Update <language-code> appropriately."
            },
            locale: {
                type: string,
                required: true,
                description: f"Translate to {locale}."
            },
        },
    }


def __ocr():
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
                    # minimum: 0,
                    # maximum: 1,
                    # multipleOf: 0.01,
                    description: "Content readability from image."
                },
            }
        }
    }


def __medical():
    return {
        "medical": {
            type: object,
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


def __retail():
    return {
        "retail": {
            type: object,
            description: "product section enabled only when meta.content is not medical; null otherwise.",
            properties: {
                "name": {
                    type: string
                }
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
    print(json.dumps(instruction_schema(), indent=4))
