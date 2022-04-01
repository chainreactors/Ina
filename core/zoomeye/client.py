from .. import logging
from ..requests import *
from ..client import Client
from settings import zoomeye_key


def request_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
        except Exception as e:
            logging.error("request error, %s" % str(e))
            return {}

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            logging.error("unauthorized")
            return {}
        elif resp.status_code == 402:
            logging.error("credits_insufficient")
            return {}
        elif resp.status_code == 403:
            logging.error("forbidden or suspended")
            return {}
        else:
            logging.error("unknown error, %d, %s" % (resp.status_code, resp.text))
            return {}
    return wrapper


class ZoomeyeClient(Client):
    maxpage = 200

    def __init__(self):
        self.status = False
        self.base_url = "https://api.zoomeye.org"
        self.auth = {"API-KEY": zoomeye_key}

    def check_login(self):
        login_url = "/resources-info"
        j = self.request(login_url)
        if j["resources"]["search"] > 1000:
            self.status = True

    def query(self, code, page=1):
        if not self.status:
            logging.error("login check failed, please check errmsg")
            return []
        search_url = "/host/search"
        param = {
            "query": code,
             "page": page,
             # "facets": fields,
             "sub_type": "sub_type:v4",
             # "s": 1000,
        }
        j = self.request(search_url, param)
        total = j.get("total", 0)
        res = j.get("matches", [])

        # 递归
        if total > 20 * page and 20 * page < self.maxpage:
            res += self.query(code, page+1)
        return res

    def filter_data(self):
        pass

    @request_handler
    def request(self, api, params=None):
        return get(self.base_url + api, headers=self.auth, params=params, debug=True)


