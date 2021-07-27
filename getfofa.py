import click
import gevent
from gevent import monkey
from gevent.pool import Pool
from operator import add
from functools import reduce
import logging

INFO_FORMAT = "%(levelname)s %(message)s"
ERROR_FORMAT = "%(levelname)s %(message)s"
logging.basicConfig(level=logging.INFO, format=INFO_FORMAT)
logging.basicConfig(level=logging.ERROR, format=ERROR_FORMAT)
monkey.patch_all()
g = Pool(100)

from fofaclient import FofaClient
from iputil import *
from favicon import get_hash
from icp import Beian,get_icp



client = FofaClient()

def get_fofa(code):
    logging.info("fofa querying "+code)
    return client.query(code)

def get_hostbyicp(icp):
    logging.info("icp querying " + icp)
    return Beian.get_host(icp)

def get_hashbyurl(url):
    logging.info("favicon requesting")
    return get_hash(url)

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

def sort_fofadata(data):
    domains = set()
    icps = set()
    urls = set()
    ips = set()
    for d in data:
        url, ip, port, domain, title, icp = d
        ips.add(ip)
        if domain:
            domains.add(domain)
        if icp:
            icps.add(icp)
        if url:
            urls.add(url)
    return ips,urls,domains,icps

def getfofaquery(fofatype,fofaquery):
    assert fofatype in ["cert","domain","ip","icon_hash"] ,"error fofa query type"
    return f'{fofatype}="{fofaquery}"'


def getvalues(gevenlets):
    return [i.value for i in gevenlets]

def get_ipanddomain(datas,ipset:set,domainset:set):
    for code,data in datas.items():
        ips, urls, domains, icps = sort_fofadata(data)
        logging.info(f"found new ips from {code}:"+str(ips-ipset))
        ipset = ipset.union(ips)
        logging.info(f"found new domains from {code}:"+str(domainset-domains))
        domainset = domainset.union(domains)
    return ipset,domainset


def main(code):
    firstdata = get_fofa(code)

    ipset,urls,domainset,icps = sort_fofadata(firstdata)
    logging.info(f"found {len(ipset)} ips, {len(domainset)} domains")
    # 获取ico hash值,通过icp获取domains
    icojobs = [g.spawn(get_hash,url) for url in urls]
    icpjobs = [g.spawn(Beian.get_host,icp) for icp in icps]
    gevent.joinall(icojobs)

    # gevent.joinall(icojobs+icpjobs)

    # 过滤ico数据
    icohashs = [i[0] for i in getvalues(icojobs) if i[0] and not i[1]]
    icohashs = [k for k, v in Counter(icohashs).items() if v >= 2]

    # 处理icp数据,过滤中文域名
    icpdomains = set(filter(lambda x:not is_contains_chinese(x) ,reduce(add, getvalues(icpjobs))))
    logging.info("found new domains from icp: "+str(icpdomains-domainset))
    domainset = domainset.union(icpdomains)

    # 第二次执行fofa
    domainjobs = {getfofaquery("domain", domain):get_fofa(getfofaquery("domain", domain)) for domain in domainset}
    certjobs = {getfofaquery("cert", domain):get_fofa(getfofaquery("cert", domain)) for domain in domainset}
    hashjobs = {getfofaquery("icon_hash", hash):get_fofa(getfofaquery("icon_hash", hash)) for hash in icohashs}

    logging.info("data processing")

    ipset,domainset = get_ipanddomain(domainjobs,ipset,domainset)
    ipset,domainset = get_ipanddomain(certjobs,ipset,domainset)
    ipset,domainset = get_ipanddomain(hashjobs,ipset,domainset)

    return ipset,domainset

if __name__ == '__main__':
    print(main('cert="mca.gov.cn"'))
