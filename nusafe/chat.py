import json

import ai
from ai import product_analysis_schema
from log_trace import Trace
from nusafe import *


@Trace
async def __on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file: File = await update.message.photo[-1].get_file()
    text = ai.gemini(product_analysis_schema("diabetes", "cholesterol"), photo_file.file_path)
    text = json.dumps(text, indent=2, ensure_ascii=False)
    await update.effective_message.reply_text(text[:4096])


application.add_handler(MessageHandler(filters.PHOTO, __on_photo))
