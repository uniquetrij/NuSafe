import logging
import os
from contextlib import suppress
from threading import Thread

import colorlog
from flask import Flask, request

import ai
import env
import nusafe
from ai import product_analysis_schema

app = Flask(__name__, static_url_path='/static', static_folder='.data/.tmp')

app.secret_key = '956b05af-047b-45d5-a31a-9b325909e172'

_log = logging.getLogger(Flask.__name__)


@app.route('/')
def root():
    return 'ok'


@app.route('/lens', methods=['POST'])
def lens():
    image = request.json.get('image', None)
    concerns = request.json.get('concerns', {})
    text = ai.gemini(product_analysis_schema(**concerns), image)

    return text


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
            if name in ['telegram.ext.Application', 'Flask']:
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
