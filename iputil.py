from ipaddress import *
from collections import Counter
from itertools import groupby

def count(data):
    return Counter(data)

def splitcidr(cidr,mask=24):
    """
    :type cidr: string
    :param cidr:
    :param mask:
    :return:
    :rtype list of IPv4Network
    """
    cidr = ip_network(cidr) # type: IPv4Network
    return list(cidr.subnets(new_prefix=mask))

def countCIDR(ips):
    '''
    :type ips: list[string]
    :param
    :return:

    统计ip在每个c段中出现的次数
    '''
    return count(map(lambda x: str(ip_network(x).supernet(prefixlen_diff=8)), ips))

def statCIDR(ips):
    """

    :param ips:
    :return:

    将ip组成的数组按照C段分类
    """
    res = {}
    for ip in ips:
        cip = ip2supernet(ip)
        if cip not in res:
            res[cip] = [ip]
        else:
            res[cip].append(ip)
    return res

def ip2supernet(ip, supernet=8):
    # 获取ip对应的C段
    return str(ip_network(ip).supernet(prefixlen_diff=supernet))



def guessCIDR(ips):
    # 统计一组ip的掩码,返回netaddress
    s = list(map(lambda x: int(x.split(".")[-1]), ips))
    maxip = max(s)
    minip = min(s)
    tmp = maxip-minip
    res = 0
    while tmp > 1:
        tmp /= 2
        res += 1

    return ip2supernet(ips[0],res)


def guessCIDRs(data):
    return [guessCIDR(v) for v in statCIDR(data).values()]

def is_ipv4(ip):
    try:
        ip_address(ip)
        return True
    except:
        return False


def sort_doaminandip(data):
    res = {k:list(g) for k,g in groupby(sorted(data),is_ipv4)}
    return res.get(True,[]),res.get(False,[])

if __name__ == '__main__':
    ips,domains = sort_doaminandip(
        ["a.com"])
    print(ips,domains)











