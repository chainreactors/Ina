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
from fofadata import FofaData



client = FofaClient()
querys = set()
def get_fofa(code):
    if code not in querys:
        logging.info("fofa querying "+code)
        querys.add(code)
        return client.query(code,isfilter=True)
    else:
        return []

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

def filter_icp(jobs):
    if jobs == None:
        return []
    return set(filter(lambda x:not is_contains_chinese(x) ,reduce(add, getvalues(jobs))))

def filter_ico(jobs):
    if jobs == None:
        return []
    icohashs = [str(i[0]) for i in getvalues(jobs) if i[0] and not i[1]]
    return [k for k, v in Counter(icohashs).items() if v >= 3]


def run_fofas(fofatype, fofaquerys,fofadata:FofaData):
    for q in fofaquerys:
        code = getfofaquery(fofatype,q)
        data = get_fofa(code)

        ips, urls, domains, icps = sort_fofadata(data)
        # 输出新出现的数据
        # if len((newips:=ips-fofadata["ip"])):
        #     logging.info(f"found {len(newips)} new ips from {code}:"+str(newips))
        # if len(newdomains:=(domains-fofadata["domain"])):
        #     logging.info(f"found {len(newdomains)} new domains from {code}:"+str(newdomains))

        fofadata.union_fofa(ips, urls, domains, icps)
    return fofadata


def run(code):
    firstdata = get_fofa(code)
    fofadata = FofaData(True,logging.info)
    ipset,urls,domainset,icps = sort_fofadata(firstdata)
    fofadata.union_fofa(ipset,urls,domainset,icps)
    logging.info(f"found {len(ipset)} ips, {len(domainset)} domains")
    # 获取ico hash值,通过icp获取domains
    icojobs = [g.spawn(get_hash,url) for url in urls]
    icpjobs = [g.spawn(Beian.get_host,icp) for icp in fofadata["icp"]]
    gevent.joinall(icojobs+icpjobs)

    # gevent.joinall(icojobs+icpjobs)

    # 过滤ico数据
    # icohashs = [str(i[0]) for i in getvalues(icojobs) if i[0] and not i[1]]
    # icohashs = [k for k, v in Counter(icohashs).items() if v >= 3]
    icohashs = filter_ico(icojobs)
    fofadata.union("ico",icohashs)


    # 处理icp数据,过滤中文域名
    icpdomains = filter_icp(icpjobs)
    ips,domains = sort_doaminandip(icpdomains)
    fofadata.union("domain",domains)
    fofadata.union("ip",ips)

    # domains = [domain for domain in fofadata["domain"] if not is_ipv4(domain)]
    ips,icos,icps,urls,domains = fofadata.getdata()
    fofadata = run_fofas("domain",domains,fofadata)
    fofadata = run_fofas("cert",domains,fofadata)

    # 再次处理ico和icp
    icojobs_d2 = [g.spawn(get_hash,url) for url in fofadata["url"]-urls]
    icpjobs = [g.spawn(Beian.get_host,icp) for icp in fofadata["icp"]-icps]
    gevent.joinall(icojobs_d2+icpjobs)

    # icohashs = [str(i[0]) for i in getvalues(icojobs) if i[0] and not i[1]]
    # icohashs = [k for k, v in Counter(icohashs).items() if v >= 3]
    icohashs = filter_ico(icojobs+icojobs_d2)
    fofadata.union("ico",icohashs)

    icpdomains = filter_icp(icpjobs)
    ips,domains = sort_doaminandip(icpdomains)
    fofadata.union("domain",domains)
    fofadata.union("ip",ips)

    fofadata = run_fofas("icon_hash",fofadata["ico"],fofadata)
    fofadata["cidr"] = guessCIDRs(fofadata["ip"])
    return fofadata


@click.command()
@click.option("--code","-c",help="fofa查询语句",prompt="input fofa query""")
@click.option("--filename","-f",help="输出文件名")
@click.option("--output","-o",default="ip,domain,cidr")
def main(code,filename,output):
    fofadata = run(code)
    # 输出的ip地址为地址段
    outputs = output.split(",")
    outdata = dict(zip(outputs,fofadata.getdata(outputs)))

    if filename:
        tmp = open(filename, "w")
        for o in outputs:
            tmp.write("\n".join(outdata[o]))
            tmp.write("\n")
        tmp.close()
    else:
        print()
        for o in outputs:
            for i in outdata[o]:
                print(i)

    while (output := click.prompt("choice output(ip,cidr,ico,icp,url,domain) or enter [exit] exit")) != "exit":
        for d in fofadata.getdata(output.split(",")):
            print("\n".join(d))



if __name__ == '__main__':
    main()
