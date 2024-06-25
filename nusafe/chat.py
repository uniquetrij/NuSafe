import json

import ai
from ai.schema import instruction_schema
from log_trace import Trace
from nusafe import *


@Trace
async def __on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file: File = await update.message.photo[-1].get_file()
    text = ai.gemini(instruction_schema(
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
    ), photo_file.file_path)
    text = json.dumps(text, indent=2, ensure_ascii=False)
    try:
        while text:
            if len(text) > 4096:
                i = text[:4096].rindex('\n')
            else:
                i = len(text)
            await update.effective_message.reply_text(text[:i].replace(' ', ' '))
            text = text[i:]
    except:
        pass




application.add_handler(MessageHandler(filters.PHOTO, __on_photo))
