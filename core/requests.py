import requests
from functools import wraps
from settings import requests_debug, is_debug, mitm_proxy
from . import logging

import urllib3
urllib3.disable_warnings()


def debug(func):
    # 如果requests中含有debug参数或setting中设置了is_debug=True 则request开启debug
    @wraps(func)
    def wrapper(url, **kwargs) -> requests.Response:
        if ("debug" in kwargs and kwargs.pop("debug")) or is_debug:
            kwargs.update(requests_debug)
        return func(url, **kwargs)
    return wrapper


def error(func):
    # requests的自动错误处理
    @wraps(func)
    def wrapper(url, **kwargs) -> requests.Response:
        try:
            return func(url, **kwargs)
        except Exception as e:
            logging.error(url + str(e))
            return None
    return wrapper


def proxy(func):
    @wraps(func)
    def wrapper(url, **kwargs):
        if "proxy" in kwargs and kwargs.pop("proxy") and "proxies" not in kwargs:
            return func(url, proxies=mitm_proxy, **kwargs)
        return func(url, **kwargs)
    return wrapper


@error
@debug
@proxy
def get(url, **kwargs) -> requests.Response:
    return requests.get(url, verify=False, **kwargs)


@error
@debug
@proxy
def post(url, **kwargs) -> requests.Response:
    return requests.post(url, verify=False, **kwargs)


@error
@debug
@proxy
def put(url, **kwargs) -> requests.Response:
    return requests.put(url, verify=False, **kwargs)


@error
@debug
@proxy
def patch(url, **kwargs) -> requests.Response:
    return requests.patch(url, verify=False, **kwargs)
