import logging
import re
import urllib3
from urllib import parse
import requests


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Beian(object):
    timeout = 5
    url = "https://m-beian.miit.gov.cn/webrec/queryRec"
    header = {
        "Host": "m-beian.miit.gov.cn",
        "Origin": "https://m-beian.miit.gov.cn",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://m-beian.miit.gov.cn/",
        "Accept-Language": "zh-cn",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "keep-alive"
    }
    domains = []

    @staticmethod
    def get_host(comp):
        comp = parse.quote(comp, encoding='utf-8')
        param = "keyword={}&pageIndex=1&pageSize=20".format(comp)
        domains = []
        with requests.post(Beian.url, data=param, headers=Beian.header, timeout=Beian.timeout,verify=False) as r:
            if r.status_code != 200:
                return
            res_json = r.json()
            total_page = res_json["result"]["totalPages"]
            content = res_json["result"]["content"]
            if not content:
                return []
            for item in content:
                domain = item["domain"]
                domains.append(domain)
            for page in range(2, int(total_page) + 1):
                domains += Beian.query_host_by_comp_page(comp,page)
            return domains

    def query_host_by_comp_page(self, comp,page):
        param = "keyword={}&pageIndex={}&pageSize=20".format(comp, page)

        with requests.post(Beian.url, data=param, headers=Beian.header, timeout=Beian.timeout,verify=False) as r:
            if r.status_code != 200:
                return []
            res_json = r.json()
            content = res_json["result"]["content"]
            if not content:
                return []

            return list(map(lambda x:x["domain"],content))

    @staticmethod
    def get_comp(comp):
        comp = parse.quote(comp, encoding='utf-8')
        param = "keyword={}&pageIndex=1&pageSize=20".format(comp)

        with requests.post(Beian.url, data=param, headers=Beian.header, timeout=Beian.timeout, verify=False) as r:
            if r.status_code != 200:
                return []
            res_json = r.json()
            content = res_json["result"]["content"]
            if not content:
                return []
            return list(map(lambda x: x["serviceName"], content))


def get_icp(url):
    try:
        r = requests.get(url,verify=False,timeout = 3)
        if len(icp := re.findall(r".ICP[备|证]\d+?号",r.text)) > 0:
            return icp
        return ""
    except:
        return ""

if __name__ == '__main__':
    print(Beian.get_host("京ICP备06050845号"))