import requests
from Fofa_moudle import settings
import base64
import json


def FofaQuery(Qstring):
    VerifyQueryUrl = "https://fofa.so/api/v1/info/my?email=${0}&key=${1}"

    Qstringb64 = base64.b64encode(Qstring.encode('utf8')).decode('utf8')

    FirstRes = requests.get(VerifyQueryUrl.format(settings.Fofa_email_company,settings.Fofa_key_company))

    try:
        FirstDict = json.loads(FirstRes.text)
    except:
        return "please check your key and email"

    SecondQueryUrl = "https://fofa.so/api/v1/search/all?email={0}&key={1}&qbase64={2}&size=100&fields=domain,ip,as_organization"

    if FirstDict["error"]:
        SecondRes = requests.get(
            SecondQueryUrl.format(settings.Fofa_email_company, settings.Fofa_key_company, Qstringb64))
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




# result = FofaQuery("app=\"ThinkPHP\" && body=\"博彩\"")
# print(result)