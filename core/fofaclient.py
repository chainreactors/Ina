import requests
import base64

from settings import *


class FofaClient:
    def __init__(self):
        self.status = False
        self.base_url = "https://fofa.so"
        self.search_api_url = "/api/v1/search/all"
        self.login_api_url = "/api/v1/info/my"
        self.auth = {"email":fofa_email,"key":fofa_key}
        self.filtercode = ' && (country="CN" && region!="HK" && region!="TW" && title!="彩票" && title!="娱乐" && title!="导航"&& title!="视频" && title!="贝壳" && title!="二手房" && title!="考试" && title!="免费" && is_fraud=false)'

        self.checkuser()

    def checkuser(self):

        j = self.request(self.login_api_url,self.auth)
        if "errmsg" in j:
            print("[-] " +j["errmsg"])
            self.status = False
            return False
        else:
            self.status = True
            return True

    def query(self,code,page=1,isfilter=False,fields="host,ip,port,domain,title,icp"):
        if isfilter:
            code = f"({code})" + self.filtercode
        param = {"qbase64": self.base64encode(code),
                 "page":page,
                 "fields":fields,
                 "size":1000,
                 }
        param.update(self.auth)
        j = self.request(self.search_api_url,param)
        if "errmsg" in j:
            print(j)
            print("[-] " +j["errmsg"])
            return []
        res = j["results"]

        # 递归
        if page*1000 < j["size"]/2 :
            res += self.query(code,page+1)
            return res
        return res

    def base64encode(self,code):
        return base64.b64encode((code).encode()).decode()

    def request(self,api,param):
        try:
            r = requests.get(self.base_url+api,params=param)
            return r.json()
        except Exception as e:
            return {"errmsg":str(e)}
