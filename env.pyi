IS_DEV: bool
DOMAIN_URL: str
STATIC_URL: str
WEBAPP_URL: str
WEBAPP_NAME: str
DATA_PATH: str
TMP_FILES_PATH: str
PERSISTENCE_PATH: str
BOT_TOKEN: str
BOT_USERNAME: str
GEMINI_KEYS: list
GEMINI_PRO: str
GEMINI_FLASH: str
GEMINI_URL: str


class schema:
    DEFAULT: dict
    PRIMARY_INSTRUCTION: str
    OCR_INSTRUCTION: str
    META_INSTRUCTION: str
    META_INDICATORS: dict
    HEALTH_INSTRUCTION: str
    HEALTH_CONCERNS_INSTRUCTION: str
    HEALTH_CONCERNS_ITEMS_INSTRUCTION: str
    HEALTH_CONCERNS_ITEMS_PRECAUTIONS_INSTRUCTION: str
    HEALTH_CONCERNS_ITEMS_PRECAUTIONS_INDICATORS_INSTRUCTION: str
    HEALTH_REPORT_INSTRUCTION: str
    HEALTH_REPORT_INDICATORS: dict
    HEALTH_DEMOGRAPTHY_INSTRUCTION: str
    HEALTH_DEMOGRAPTHY_INDICATORS: dict
    HEALTH_VITALS_INSTRUCTION: str
    HEALTH_VITALS_INDICATORS: dict
    HEALTH_CONCERNS_INGREDIENT_INDICATORS: dict
    HEALTH_CONCERNS_ITEMS_INDICATORS: dict
    PRODUCT_INSTRUCTION: str
    PRODUCT_GENERIC_INSTRUCTION: str
    PRODUCT_ALLERGENS_INSTRUCTION: str
    PRODUCT_ALLERGENS_ITEM_INSTRUCTION: str
    PRODUCT_ACUTES_INSTRUCTION: str
    PRODUCT_ACUTES_ITEM_INSTRUCTION: str
    PRODUCT_CHRONICS_INSTRUCTION: str
    PRODUCT_CHRONICS_ITEM_INSTRUCTION: str
    PRODUCT_SPECIFIC_INSTRUCTION: str
    PRODUCT_SPECIFIC_MEMBER_INSTRUCTION: str
    PRODUCT_SPECIFIC_MEMBER_CONCERN_INSTRUCTION: str
    PRODUCT_ITEM_INSTRUCTION: str
    PRODUCT_ITEM_INDICATORS: dict
    CONSTITUENTS_INSTRUCTION: str
    CONSTITUENTS_ITEM_INSTRUCTION: str
    CONSTITUENTS_ITEM_INDICATORS: dict
BOT_MENTION_MD: str
BOT_MENTION: str
