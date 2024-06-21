import dis
import linecache
import logging
import re
import sys
from functools import wraps
from sys import settrace
from types import FunctionType, FrameType
from typing import TypeVar, Callable, Union

from colorlog import ColoredFormatter

F = TypeVar('F', bound=Callable[..., int])
logging.addLevelName(5, 'TRACE')


class Trace:
    from enum import Enum

    class EVENTS(Enum):
        CALL = 'call'
        LINE = 'line'
        EXCEPTION = 'exception'
        RETURN = 'return'
        VAR = 'var'
        CALL_LINE = 'call;line'
        CALL_EXCEPTION = 'call;exception'
        CALL_RETURN = 'call;return'
        CALL_VAR = 'call;var'
        LINE_EXCEPTION = 'line;exception'
        LINE_RETURN = 'line;return'
        LINE_VAR = 'line;var'
        EXCEPTION_RETURN = 'exception;return'
        EXCEPTION_VAR = 'exception;var'
        RETURN_VAR = 'return;var'
        CALL_LINE_EXCEPTION = 'call;line;exception'
        CALL_LINE_RETURN = 'call;line;return'
        CALL_LINE_VAR = 'call;line;var'
        CALL_EXCEPTION_RETURN = 'call;exception;return'
        CALL_EXCEPTION_VAR = 'call;exception;var'
        CALL_RETURN_VAR = 'call;return;var'
        LINE_EXCEPTION_RETURN = 'line;exception;return'
        LINE_EXCEPTION_VAR = 'line;exception;var'
        LINE_RETURN_VAR = 'line;return;var'
        EXCEPTION_RETURN_VAR = 'exception;return;var'
        CALL_LINE_EXCEPTION_RETURN = 'call;line;exception;return'
        CALL_LINE_EXCEPTION_VAR = 'call;line;exception;var'
        CALL_LINE_RETURN_VAR = 'call;line;return;var'
        CALL_EXCEPTION_RETURN_VAR = 'call;exception;return;var'
        LINE_EXCEPTION_RETURN_VAR = 'line;exception;return;var'
        ALL = 'call;line;exception;return;var'

    __trk: set = set()
    __fns: dict = dict()
    __stk: list = list()
    __log = None
    __handler = None

    __vre = re.compile("([a-zA-Z_]\w*)['\[(\w)\]]*(?:\s*,\s*([a-zA-Z_]\w*)['\[(\w)\]]*)*\s*=\s*[^=]")
    __fmt: str = '%(asctime)s %(log_color)s%(levelname)8s%(reset)s %({})s%(trace_info)s {} %(reset)s%({})s%(line)s%(message)s%(reset)s'
    __dtf: str = '%Y-%m-%d %H:%M:%S'

    __fmt_call = None
    __fmt_line = None
    __fmt_exception = None
    __fmt_return = None
    __fmt_var = None

    @property
    def TRACE(self) -> int:
        return 5

    @classmethod
    def __fmt_bld(cls, sy, c1, c2='white', c0='light_yellow'):
        return ColoredFormatter(
            fmt=cls.__fmt.format(c1, sy, c2),
            datefmt=cls.__dtf,
            log_colors={
                'TRACE': c0
            })

    @classmethod
    def is_running_debugger(cls):
        return hasattr(sys, 'gettrace') and bool(sys.gettrace()) or sys.breakpointhook.__module__ != "sys"

    def __new__(cls, *args):
        if cls.is_running_debugger():
            return

        if cls.__log is None:
            cls.__setup_handler()
            settrace(Trace.__tracer)

        fn, events, var_names = cls.__extract_params(args)

        def decorator(function: Union[FunctionType, Callable]) -> F:
            cls.__fns[f'{function.__module__}.{function.__name__}'] = (events, var_names)

            @wraps(function)
            def wrapper(*_args, **_kwargs):
                return function(*_args, **_kwargs)

            return wrapper

        if fn:
            return decorator(fn)
        else:
            return decorator

    @classmethod
    def __setup_handler(cls):
        cls.__handler = logging.StreamHandler()
        cls.__log = logging.getLogger(__name__)
        cls.__log.propagate = False
        cls.__log.addHandler(cls.__handler)
        cls.__log.setLevel('TRACE')
        cls.__log.trace = lambda *__args, **__kwargs: cls.__log.log(5, *__args, **__kwargs)
        cls.__fmt_call = cls.__fmt_bld('↪', 'blue')
        cls.__fmt_line = cls.__fmt_bld('⇌', 'cyan')
        cls.__fmt_exception = cls.__fmt_bld('⤰', 'red')
        cls.__fmt_return = cls.__fmt_bld('↩', 'purple')
        cls.__fmt_var = cls.__fmt_bld('≫', 'yellow')

    @classmethod
    def __extract_params(cls, args):
        if args:
            if callable(args[0]):
                fn = args[0]
                events = cls.EVENTS.CALL_EXCEPTION_RETURN.value
                var_names = []
            elif isinstance(args[0], cls.EVENTS):
                fn = None
                events = args[0].value
                var_names = args[1:] if len(args) > 1 else []
            elif not set(args[0].split(';')).isdisjoint(cls.EVENTS.ALL.value.split(';')):
                fn = None
                events = args[0]
                var_names = args[1:] if len(args) > 1 else []
            else:
                fn = None
                events = cls.EVENTS.VAR.value
                var_names = args
        else:
            fn = None
            events = cls.EVENTS.ALL.value
            var_names = []
        return fn, events, var_names

    @classmethod
    def __tracer(cls, frame: FrameType, event: str, arg):
        cls.__log_vars()

        module = frame.f_globals.get("__name__") or ''
        function = frame.f_code.co_name

        if f'{module}.{function}' not in cls.__fns.keys():
            return

        events, var_names = cls.__fns[f'{module}.{function}']

        line_no = frame.f_lineno

        trace_info = f'[{line_no:>5}]:{module}.{function}'

        filename = frame.f_code.co_filename
        line = linecache.getline(filename, line_no, frame.f_globals).strip()

        if event == 'call':
            if line_no != frame.f_code.co_firstlineno:
                return
        if event == 'exception':
            if 'await' in line and arg and arg[0] == StopIteration:
                return
        if event == 'return':
            if 'return' in line:
                if 'await' in line:
                    if (frame, True) in cls.__trk:
                        cls.__trk.remove((frame, True))
                    else:
                        cls.__trk.add(frame)
                        return
                elif frame.f_back in cls.__trk:
                    cls.__trk.remove(frame.f_back)
                    cls.__trk.add((frame.f_back, True))
            else:
                if 'await' in line:
                    if frame.f_lasti != list(dis.get_instructions(frame.f_code))[-1].offset:
                        return

        if event in events:
            cls.__log_events(arg, event, frame, function, line, module, trace_info)

        if cls.EVENTS.VAR.value in events:
            matches = cls.__vre.findall(line.strip())
            if matches:
                for match in matches:
                    for var_name in match:
                        if var_name in var_names:
                            cls.__stk.append((var_name, frame.f_locals, trace_info))

        return cls.__tracer

    @classmethod
    def __log_events(cls, arg, event, frame, function, line, module, trace_info):
        match event:
            case 'call':
                cls.__handler.setFormatter(cls.__fmt_call)
            case 'line':
                cls.__handler.setFormatter(cls.__fmt_line)
            case 'exception':
                cls.__handler.setFormatter(cls.__fmt_exception)
            case 'return':
                cls.__handler.setFormatter(cls.__fmt_return)
        args = {}
        for i in range(frame.f_code.co_argcount):
            name = frame.f_code.co_varnames[i]
            value = frame.f_locals[name]
            try:
                args[name] = str(value)
            except AttributeError:
                args[name] = AttributeError((module, function, name, type(value)))
        cls.__log.trace(
            f'{(args if args else "") if event == "call" else (str(arg).replace(chr(10), "␤") if arg else "")}',
            extra={
                'trace_info': trace_info,
                'line': f'{line} ' if event == 'line' else ''
            }
        )

    @classmethod
    def __log_vars(cls):
        if cls.__stk:
            cls.__handler.setFormatter(cls.__fmt_var)
            var_name, f_locals, trace_info = cls.__stk.pop()
            if var_name in f_locals:
                cls.__log.trace(
                    f'{var_name} ≔ {f_locals[var_name]}',
                    extra={
                        'trace_info': trace_info,
                        'line': ''
                    })
