import requests
from settings import *
import base64
import json
import fofa


def FofaQuery(Qstring):
    VerifyQueryUrl = "https://fofa.so/api/v1/info/my?email={0}&key={1}"

    Qstringb64 = base64.b64encode(Qstring.encode('utf8')).decode('utf8')

    FirstRes = requests.get(VerifyQueryUrl.format(fofa_email,fofa_key))
    print(VerifyQueryUrl.format(fofa_email,fofa_key))
    try:
        FirstDict = json.loads(FirstRes.text)
    except:
        return "please check your key and email"

    SecondQueryUrl = "https://fofa.so/api/v1/search/all?email={0}&key={1}&qbase64={2}&size=100&fields=domain,ip,as_organization"

    if FirstDict["error"]:
        SecondRes = requests.get(
            SecondQueryUrl.format(fofa_email, fofa_key, Qstringb64))
        SecondDict = json.loads(SecondRes.text)
        SumDict = dict()
        InfoList = SecondDict["results"]
        # for info in InfoList:
        #     ip = info[1]
        #     host = info[0]
        #     port = info[2]
        #     if ip not in SumDict.keys():
        #         SumDict[ip] = list()
        #         SumDict[ip].append(host)
        #     else:
        #         SumDict[ip].append(host)
        # for hosts in SumDict.values():
        #     hosts = list(set(hosts))
        return InfoList

    else:
        return "something error please check your query string"

if __name__ == '__main__':
    fofa.Client(fofa_email,fofa_key)

# result = FofaQuery("app=\"ThinkPHP\" && body=\"博彩\"")
# print(result)