import json

import ai
from ai import product_analysis_schema
from log_trace import Trace
from nusafe import *


@Trace
async def __on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file: File = await update.message.photo[-1].get_file()
    text = ai.gemini(product_analysis_schema(
        chronic=env.schemas.CHRONIC, acute=env.schemas.ACUTE, allergies=env.schemas.ALLERGY), photo_file.file_path)
    text = json.dumps(text, indent=4, ensure_ascii=False)
    try:
        while text:
            if len(text) > 4096:
                i = text[:4096].rindex('\n')
            else:
                i = len(text)
            print(text[:i], len(text[i:]))
            await update.effective_message.reply_text(text[:i].replace(' ', ' '))
            text = text[i:]
    except:
        pass




application.add_handler(MessageHandler(filters.PHOTO, __on_photo))
