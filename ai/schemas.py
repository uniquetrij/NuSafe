import json

import env


def get_conditions(group):
    match group:
        case 'chronic':
            return env.CHRONIC_CONDITIONS
        case 'acute':
            return env.ACUTE_CONDITIONS


def get_product_analysis_schema(group_conditions: dict[list] | None = None) -> str:
    if group_conditions is None:
        group_conditions = {'chronic': env.CHRONIC_CONDITIONS, 'acute': env.ACUTE_CONDITIONS, 'allergen': env.ALLERGENS}
    schema = {
        # "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "description": "health conditions and allergic reactions that could be afflicted by product ingredients.",
        "properties": {group: {
            "type": "object",
            "description": "",
            "properties": {
                condition: {
                    "type": "object",
                    "description": f"product affliction profile for {condition}.",
                    "properties": {
                        "risk": {
                            "type": "number",
                            "description": f"probability (0, 1) that this product could potentially afflict {condition}; 0 is low risk, 1 is high risk."
                        },
                        "ingredients": {
                            "type": "array",
                            "description": f"ingredients afflicting {condition}.",
                            "items": {
                                "type": "object",
                                "description": f"an ingredient afflicting {condition}.",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": f"name of ingredient afflicting {condition}."
                                    },
                                    "proportion": {
                                        "type": "number",
                                        "description": f"fraction of this ingredient present in this product by mass."
                                    },
                                    "potency": {
                                        "type": "number",
                                        "description": f"probability (0, 1) that this ingredient of above proportion could potentially afflict {condition}; 0 is low risk, 1 is high risk."
                                    }
                                }
                            }
                        },
                        "justification": {
                            "type": "string",
                            "description": f"justification for arriving at this rating for {condition}"
                        }
                    }

                } for condition in conditions
            }

        } for group, conditions in group_conditions.items()}
    }
    schema["properties"].update({
        "isValid": {
            "type": "boolean",
            "description": "whether the provided image contains valid product information, ingredients or nutritional facts."
        }
    })
    return json.dumps(schema, indent=2)
