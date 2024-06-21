def product_analysis_schema(*items: str, **categorized_items: set[str] | tuple[str] | list[str]) -> dict:
    if items and categorized_items:
        categorized_items[''] = items
    elif items:
        categorized_items = {"": items}
    else:
        categorized_items = {}

    schema = {
        # "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "description": "health conditions and allergic reactions that could be afflicted "
                       "by product ingredients.",
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
                            "description": f"probability (0, 1) that this product could "
                                           f"potentially afflict {condition}; "
                                           f"0 is low risk, 1 is high risk."
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
                                        "description": f"name of ingredient afflicting "
                                                       f"{condition}."
                                    },
                                    "proportion": {
                                        "type": "number",
                                        "description": f"fraction of this ingredient present "
                                                       f"in this product by mass."
                                    },
                                    "potency": {
                                        "type": "number",
                                        "description": f"probability (0, 1) that this ingredient "
                                                       f"of above proportion could potentially "
                                                       f"afflict {condition}; "
                                                       f"0 is low risk, 1 is high risk."
                                    }
                                }
                            }
                        },
                        "justification": {
                            "type": "string",
                            "description": f"justification for arriving at this rating for "
                                           f"{condition}"
                        }
                    }
                } for condition in set(conditions)
            }
        } for group, conditions in categorized_items.items()}
    }
    schema["properties"].update({
        "isValid": {
            "type": "boolean",
            "description": "whether the provided image contains valid product information, "
                           "ingredients or nutritional facts; "
                           "false otherwise; null if it can't be determined."
        },
        "hasNutritionFacts": {
            "type": "boolean",
            "description": "whether Nutrition / Supplement Facts regarding the product is "
                           "present in the image; "
                           "false otherwise; null if it can't be determined."
        },
        "hasIngredientsList": {
            "type": "boolean",
            "description": "whether Ingredients List regarding the product is present in "
                           "the image; "
                           "false otherwise; null if it can't be determined."
        },
        "isEdible": {
            "type": "boolean",
            "description": "whether the product is an edible food item; "
                           "false otherwise; null if it can't be determined."
        },
        "isCosmetic": {
            "type": "boolean",
            "description": "whether the product is a cosmetic item; "
                           "false otherwise; null if it can't be determined."
        },
        "isDrug": {
            "type": "boolean",
            "description": "whether the product is a medical drug; "
                           "false otherwise; null if it can't be determined."
        },
        "productCategory": {
            "type": "string",
            "description": "product category of this product if isEdible is true; "
                           "false otherwise; null if it can't be determined."
        },
        "dietaryCategory": {
            "type": "string",
            "enum": ["Vegetarian", "Non-Vegetarian", "null"],
            "description": "dietary category of this product if isEdible is true; "
                           "false otherwise; null if it can't be determined."

        }
    })
    return schema
