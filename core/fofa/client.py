import base64

from ..requests import get
from .. import logging
from ..client import Client
from settings import fofa_key, fofa_email


def request_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
            j = resp.json()
        except Exception as e:
            logging.error("fofa request error, " + str(e))
            return {}

        err = j.get('error', False)
        if not err:
            return resp.json()
        else:
            logging.error("fofa error: " + j.get("errmsg", ""))
            return {}
    return wrapper


class FofaClient(Client):
    def __init__(self):
        self.status = False
        self.base_url = "https://fofa.info"
        self.auth = {"email": fofa_email, "key": fofa_key}
        self.filtercode = ' && (country="CN" && is_fraud=false)'
        self.check_login()

    def check_login(self):
        login_api_url = "/api/v1/info/my"
        json = self.request(login_api_url)
        if json.get('isvip', False):
            self.status = True

    def query(self, code, page=1, isfilter=False, fields="host,ip,port,domain,title,icp"):
        search_api_url = "/api/v1/search/all"

        # if not self.status:
        #     logging.error("login check failed, please check errmsg")
        #     return []

        if isfilter:
            code = f"({code})" + self.filtercode
        param = {
            "qbase64": self.encode(code),
            "page": page,
            "fields": fields,
            "size": 1000,
        }

        json = self.request(search_api_url, param)
        if not json:
            return []
        if "errmsg" in json:
            logging.error(json)
            logging.error("[-] " + json["errmsg"])
            return []
        res = json["results"]

        # 递归
        if page * 1000 < json.get("size", 0) / 2:
            res += self.query(code, page + 1)
            return res
        return res

    def encode(self, code):
        return base64.b64encode(code.encode()).decode()

    @request_handler
    def request(self, api, param={}):
        param.update(self.auth)
        resp = get(self.base_url + api, params=param)
        return resp
