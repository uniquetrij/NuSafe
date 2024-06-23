import logging
import os
from contextlib import suppress
from threading import Thread

import colorlog
from flask import Flask, request

import env
import nusafe

app = Flask(__name__, static_url_path='/static', static_folder='.data/.tmp')


@app.route('/')
def root():
    return 'ok'


if __name__ == '__main__':

    colorlog.basicConfig(
        format='%(asctime)s %(log_color)s%(levelname)8s%(reset)s %(light_black)s[%(lineno)5s]:%(module)s.%(funcName)s ↯ %(reset)s%(white)s%(message)s%(reset)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
    )

    with suppress(FileExistsError):
        os.mkdir(env.DATA_PATH)

    if env.IS_DEV:
        logging.getLogger("httpx").setLevel(logging.WARNING)

        for name in logging.root.manager.loggerDict:
            if name in ['telegram.ext.Application']:
                logging.getLogger(name).setLevel(logging.DEBUG)

        for folder in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            if os.path.isfile(os.path.join(folder, '__init__.py')):
                logging.getLogger(folder).setLevel(logging.DEBUG)

    Thread(target=app.run, daemon=True).start()

    try:
        nusafe.application.run_polling()
    except TypeError:
        os.remove(env.PERSISTENCE_PATH)
        nusafe.application.run_polling()
