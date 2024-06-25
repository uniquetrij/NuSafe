import logging
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules

# noinspection PyUnresolvedReferences
from telegram import *
# noinspection PyUnresolvedReferences
from telegram.constants import *
# noinspection PyUnresolvedReferences
from telegram.ext import *
# noinspection PyUnresolvedReferences
from telegram.helpers import *

import env

log = logging.getLogger(__name__)


def __load():
    if __name__ == 'main':
        raise
    import_module(f"{__name__}")
    package_dir = Path(__file__).resolve().parent
    for (_, module_name, _) in iter_modules([str(package_dir)]):
        # import the module and iterate through its attributes
        module = import_module(f"{__name__}.{module_name}")
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isclass(attribute):
                # Add the class to this package's variables
                globals()[attribute_name] = attribute


async def __setup_bot(bot: ExtBot):
    # await bot.set_my_description('')
    # await bot.set_chat_menu_button(
    #     menu_button=MenuButtonWebApp(
    #         env.WEBAPP_NAME, WebAppInfo()
    #     ))

    pass


async def __post_init(app: Application):
    bot: ExtBot = app.bot
    # noinspection PyCallingNonCallable
    env(BOT_MENTION_MD=f'[{bot.username}](tg://user?id={bot.id})')
    # noinspection PyCallingNonCallable
    env(BOT_MENTION=f'{bot.name}')

    await __setup_bot(bot)

    __load()


application: Application = Application.builder() \
    .token(env.BOT_TOKEN) \
    .post_init(__post_init) \
    .persistence(PicklePersistence(env.PERSISTENCE_PATH)) \
    .arbitrary_callback_data(True) \
    .build()


def lang_change_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, _lang: str):
    context.chat_data.update({'_lang': _lang})
