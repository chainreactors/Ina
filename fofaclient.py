import requests
import base64

from settings import *


class FofaClient:
    def __init__(self):
        self.status = False
        self.base_url = "https://fofa.so"
        self.search_api_url = "/api/v1/search/all"
        self.login_api_url = "/api/v1/info/my"
        self.checkuser()
        self.filtercode = 'country="CN" && region!="HK" && region!="TW" && title!="彩票" && title!="娱乐" && title!="导航"&& title!="视频" && title!="贝壳" && title!="二手房" && title!="考试" && title!="免费" &&'

    def checkuser(self):
        param = {"email":fofa_email,"key":fofa_key}
        j = self.request(self.login_api_url,param)
        if "errmsg" in j:
            print("[-] " +j["errmsg"])
            self.status = False
            return False
        else:
            self.status = True
            return True

    def query(self,code,page=1,fields="host,ip,port,domain,title,icp"):

        param = {"qbase64":base64.b64encode((code).encode()).decode(),"email":fofa_email,"key":fofa_key,"page":page,"fields":fields,"size":1000}
        j = self.request(self.search_api_url,param)
        if "errmsg" in j:
            print("[-] " +j["errmsg"])
            return []
        res = j["results"]

        # 递归
        if page*1000 < j["size"]/2 :
            res += self.query(code,page+1)
            return res
        return res

    def request(self,api,param):
        try:
            r = requests.get(self.base_url+api,params=param)
            return r.json()
        except:
            return False


if __name__ == '__main__':
    fc = FofaClient()
    fc.query('icon_hash="2075065848"')