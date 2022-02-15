from collections import Counter
from ipaddress import *
from itertools import groupby
from socket import gethostbyname


def count(data):
    return Counter(data)


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def write2file(string,filename):
    tmp = open(filename, "a+",encoding="utf-8")
    tmp.write(string)
    tmp.close()


class IPs:
    def __init__(self, ips):
        if isinstance(ips,str):
            self.ips = [ips]
        else:
            self.ips = ips

    def count_cidr(self):
        '''
        :type ips: list[string]
        :param
        :return:

        统计ip在每个c段中出现的次数
        '''
        return count(map(lambda x: str(ip_network(x, strict=False).supernet(prefixlen_diff=8)), self.ips))

    def stat_cidr(self):
        """
        :param ips:
        :return:
        将ip组成的数组按照C段分类
        """
        res = {}
        for ip in self.ips:
            if not is_ipv4(ip):
                continue
            cip = ip2supernet_str(ip, 8)
            if cip not in res:
                res[cip] = [ip]
            else:
                res[cip].append(ip)
        return res

    def guess_cidrs(self):
        return [guessCIDR(v) for v in self.stat_cidr().values()]


def splitcidr(cidr,mask=24):
    """
    :type cidr: string
    :param cidr:
    :param mask:
    :return:
    :rtype list of IPv4Network
    """
    cidr = ip_network(cidr, strict=False) # type: IPv4Network
    return list(cidr.subnets(new_prefix=mask))


def countCIDR(ips):
    '''
    :type ips: list[string]
    :param
    :return:

    统计ip在每个c段中出现的次数
    '''
    return count(map(lambda x: str(ip_network(x, strict=False).supernet(prefixlen_diff=8)), ips))


def statCIDR(ips):
    """
    :param ips:
    :return:
    将ip组成的数组按照C段分类
    """
    res = {}
    for ip in ips:
        if not is_ipv4(ip):
            continue
        cip = ip2supernet_str(ip, 8)
        if cip not in res:
            res[cip] = [ip]
        else:
            res[cip].append(ip)
    return res


def contain_ip(cidr,ip):
    _cidr = ip_network(cidr, strict=False) # type: IPv4Network
    _ip = ip_address(ip)
    if _ip in _cidr:
        return True
    return False


def ip2supernet_str(ip, diffmask=0, newmask=32):
    return str(ip2supernet_netaddress(ip, diffmask, newmask))


def ip2supernet_netaddress(ip, diffmask=0, newmask=32):
    if diffmask:
        return ip_network(ip, strict=False).supernet(prefixlen_diff=diffmask)
    else:
        return ip_network(ip, strict=False).supernet(new_prefix=newmask)


def guessCIDR(ips):
    # 统计一组ip的掩码,返回netaddress
    s = sorted(ips, key=lambda x: int(x.split(".")[-1]))
    minip, maxip = s[0] ,s[-1]
    _minip = ip_address(minip)
    for i in range(9):
        if _minip in ip2supernet_netaddress(maxip, i):
            return ip2supernet_str(maxip, i)


def guessCIDRs(ips):
    return [guessCIDR(v) for v in statCIDR(ips).values()]


def updateCIDR(cidr,ip):
    _cidr = ip_network(cidr, strict=False) # type: IPv4Network
    _ip = ip_address(ip)
    if _ip in _cidr:
        return str(_cidr)
    for mask in range(_cidr.prefixlen-1, 23, -1):
        if _ip in ip2supernet_netaddress(cidr, newmask=mask):
            return ip2supernet_str(cidr, newmask=mask)
    return cidr


def updatesCIDR(cidr, ips):
    s = sorted(ips,key=lambda x: int(x.split(".")[-1]))
    minip, maxip = s[0] ,s[-1]
    cidr = updateCIDR(cidr,minip)
    cidr = updateCIDR(cidr,maxip)
    return cidr


def is_ipv4(ip):
    try:
        ip = ip_address(ip)
        if ip.version == 4:
            return True
        else:
            return False
    except:
        return False


def resolve_ip(ip):
    try:
        return gethostbyname(ip)
    except:
        return ""


def sort_doaminandip(data):
    res = {k:list(g) for k,g in groupby(sorted(data),is_ipv4)}
    return res.get(True,[]),res.get(False,[])


def count_ip(ip):
    ip = ip_network(ip, strict=False)
    return ip.num_addresses


if __name__ == '__main__':
    print(count_ip("192.1.1.2/24"))












