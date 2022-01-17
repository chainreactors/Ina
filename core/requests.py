import requests
from functools import wraps
from settings import requests_debug, is_debug
import logging
import traceback
import urllib3


urllib3.disable_warnings()


def __debug(func):
    # 如果requests中含有debug参数或setting中设置了is_debug=True 则request开启debug
    @wraps(func)
    def wrapper(url, **kwargs):
        if ("debug" in kwargs and kwargs.pop("debug")) or is_debug:
            return func(url, **requests_debug, **kwargs)
        return func(url, **kwargs)
    return wrapper


def __error(func):
    # requests的自动错误处理
    @wraps(func)
    def wrapper(url, **kwargs):
        try:
            return func(url, **kwargs)
        except Exception as e:
            logging.error(traceback.print_exc())
            return
    return wrapper


@__error
@__debug
def get(url, **kwargs):
    return requests.get(url, **kwargs)


@__error
@__debug
def post(url, **kwargs):
    requests.post(url, **kwargs)


@__error
@__debug
def put(url, **kwargs):
    requests.put(url, **kwargs)


@__error
@__debug
def patch(url, **kwargs):
    requests.patch(url, **kwargs)