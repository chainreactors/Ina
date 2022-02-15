import base64
import logging

from ..requests import *
from settings import fofa_key, fofa_email


def request_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
            j = resp.json()
        except Exception as e:
            logging.error("request error, " + str(e))
            return {}

        err = j.get('error', False)
        if not err:
            return resp.json()
        else:
            logging.error("error: " + j.get("error", ""))
            return {}
    return wrapper


class FofaClient:
    def __init__(self):
        self.status = False
        self.base_url = "https://fofa.info"
        self.auth = {"email": fofa_email, "key": fofa_key}
        self.filtercode = ' && (country="CN" && region!="HK" && region!="TW" && title!="彩票" && title!="娱乐" && title!="导航"&& title!="视频" && title!="贝壳" && title!="二手房" && title!="考试" && title!="免费" && is_fraud=false)'

        self.check_login()

    def check_login(self):
        login_api_url = "/api/v1/info/my"
        json = self.request(login_api_url, self.auth)
        if json.get('isvip', False):
            self.status = True

    def query(self, code, page=1, isfilter=False, fields="host,ip,port,domain,title,icp"):
        search_api_url = "/api/v1/search/all"

        if not self.status:
            logging.error("login check failed, please check errmsg")
            return []

        if isfilter:
            code = f"({code})" + self.filtercode
        param = {
            "qbase64": self.base64encode(code),
            "page": page,
            "fields": fields,
            "size": 1000,
        }
        param.update(self.auth)
        json = self.request(search_api_url, param)
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

    def base64encode(self, code):
        return base64.b64encode((code).encode()).decode()

    @request_handler
    def request(self, api, param):
        resp = get(self.base_url + api, params=param)
        return resp