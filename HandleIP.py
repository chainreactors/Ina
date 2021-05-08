import re
from urllib.parse import urlparse


def Getport(url):
    res = url.split(":")
    if url.startswith("http"):
        if len(res) > 2:
            return res[2]
        elif url.startswith("https"):
            return "443"
        else:
            return 80
    else:
        if len(res) > 1:
            return res[1]


def IPorDoamin(url):
    ipv4 = "((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}"
    pattern = re.compile(ipv4)
    res = pattern.search(url)
    if res is not None:
        return True
    else:
        return False


def HandleInfo(pre):
    HandledDict = dict()

    for ip, infos in pre.items():
        HandledDict[ip] = dict()
        host = list()
        IpPort = list()
        for info in infos:
            if IPorDoamin(info):
                port = Getport(info)
                if port is None:
                    port = 80
                IpPort.append(port)
            else:
                host.append(info)
        host = list(set(host))
        IpPort = list(set(IpPort))
        HandledDict[ip]["Host"] = host
        HandledDict[ip]["IpPort"] = IpPort
    return HandledDict


def HandleHost(host):
    if not host.startswith("http"):
        host = "http://" + host
    parsed = urlparse(host)
    host = parsed.netloc
    host_list = host.split(":")
    if len(host_list) == 2:
        host = host_list[0]
    else:
        host = host
    return host


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False
