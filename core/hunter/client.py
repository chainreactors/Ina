import time
from base64 import b64encode

from .. import logging
from ..client import Client
from ..requests import get
from settings import hunter_key


def request_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
            j = resp.json()
        except Exception as e:
            logging.error("hunter request error, %s" % str(e))
            return {}

        if j["code"] in [200, 400, 40205]:
            return j
        elif j["code"] == 401:
            logging.error("hunter unauthorized")
            return {}
        else:
            logging.error("hunter unknown error, %d, %s" % (resp.status_code, resp.text))
            return {}
    return wrapper


class HunterClient(Client):
    def __init__(self):
        self.status = False
        self.base_url = "https://hunter.qianxin.com/"

    def check_login(self):
        api = "openApi/search"
        if self.request:
            self.status = True

    def query(self, code:str, page=1):
        api = "openApi/search"
        param = {
            "page_size": 100,
            "search": b64encode(code.encode()),
            "page": page,
            "is_web": 3
        }

        j = self.request(api, param)
        if j.get("code", 500) != 200:
            return []

        res = j["data"].get("arr", [])
        if page * 100 < j["data"]["total"]:
            res += self.query(code, page + 1)
        return res

    @request_handler
    def request(self, api, param):
        param["api-key"] = hunter_key
        time.sleep(2)
        return get(self.base_url + api, params=param)
