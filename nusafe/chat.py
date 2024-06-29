import ai
from ai.schema import instruction_schema
from log_trace import Trace
from nusafe import *


# @Trace
# async def __on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     photo_file: File = await update.message.photo[-1].get_file()
#     text = ai.gemini(instruction_schema(
#         mother={
#             "vitals": {
#                 "age": "65",
#                 "sex": "female"
#             },
#             "concerns": {
#                 "diabetes": 0.5,
#                 "cholesterol": 0.9,
#             }
#         },
#         father={
#             "vitals": {
#                 "age": "70",
#                 "sex": "male"
#             },
#             "concerns": {
#                 "hypertension": 1,
#             }
#         },
#         wife={
#             "vitals": {
#                 "age": "25",
#                 "sex": "female"
#             },
#             "concerns": {
#                 "pregnant": 1,
#             }
#         },
#     ), photo_file.file_path)
#     text = json.dumps(text, indent=2, ensure_ascii=False)
#     try:
#         while text:
#             if len(text) > 4096:
#                 i = text[:4096].rindex('\n')
#             else:
#                 i = len(text)
#             await update.effective_message.reply_text(text[:i].replace(' ', ' '))
#             text = text[i:]
#     except:
#         pass

@Trace
async def __on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_chat_action(ChatAction.TYPING)
    photo_file: File = await update.message.photo[-1].get_file()
    result: dict = ai.openai(instruction_schema(), photo_file.file_path)

    if result['meta']['description']:
        message = f'''Type: {result['meta']['description'].capitalize()}\n'''
        message += escape_markdown(f'''Quality: {int(result['meta']['legibility'] * 100)}%\n''', 2)
        if result['meta']['description'] != 'medical':
            message += '''\n__**Allergens Present**__\n'''

            for i, item in enumerate(result['retail']['generic']['allergens']):
                message += escape_markdown(f'''{i + 1}. {item['name'].capitalize()}\n''', 2)

            message += '''\n__**Health Concerns**__\n'''

            for i, item in enumerate(result['retail']['generic']['chronic'] + result['retail']['generic']['acute']):
                message += escape_markdown(f'''{i + 1}. {item['name'].capitalize()}\n''', 2)
        else:
            message += '''\n__**Take Precautions**__\n'''

            for i, item in enumerate(result['medical']['precautions']):
                message += escape_markdown(f'''{i + 1}. {item['name'].capitalize()}\n''', 2)
    else:
        message = "Sorry, I couldn't recognize the image\."
    await update.effective_message.reply_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN_V2
    )


application.add_handler(MessageHandler(filters.PHOTO, __on_photo))
