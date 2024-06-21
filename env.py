import ast
import re
import sys
from contextlib import suppress
from dataclasses import dataclass
from types import ModuleType
from typing import Any

from dotenv import dotenv_values, find_dotenv


def __convert_value(value: Any | None):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        pass

    return re.sub(r'\s+', ' ', value).strip()


@dataclass
class __(ModuleType):

    @staticmethod
    def __raise_value_error(_, __):
        raise ValueError('env values are immutable')

    @staticmethod
    def __update(source, env_values: dict, initializing: bool = False, prefix: str = None):
        i = 0
        with open(__file__ + 'i', 'w' if initializing else 'a') as f:
            if prefix:
                f.write('\n\n')
                for cls in prefix.split('.'):
                    f.write(f'{" " * 4 * i}class {cls}:\n')
                    i += 1

            for k, v in env_values.items():
                source[k] = __convert_value(v)
                if prefix is not None or k != '.include':
                    f.write(f'{" " * 4 * i}{k}: {type(source[k]).__name__}\n')

    __setattr__ = __raise_value_error
    __update(vars(), dotenv_values(), True)
    for include in vars().get('.include', []):
        __update(
            vars(),
            dotenv_values(find_dotenv(include)),
            prefix=include.replace('.env.', '')
        )
        with suppress(Exception):
            del vars()['.include']

    def __call__(self, env_values: dict = None, **kwargs):
        """This method allows setting env variables at runtime."""

        if env_values:
            self.__update(globals(), env_values)
        self.__update(globals(), kwargs)
        return self

    def __init__(self):
        super().__init__(__name__)


sys.modules[__name__].__class__ = __
