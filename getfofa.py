import click
import gevent
from gevent import monkey
from gevent.pool import Pool
from functools import partial
import logging


INFO_FORMAT = "%(levelname)s %(message)s"
ERROR_FORMAT = "%(levelname)s %(message)s"
logging.basicConfig(level=logging.INFO, format=INFO_FORMAT)
logging.basicConfig(level=logging.ERROR, format=ERROR_FORMAT)
monkey.patch_all()
g = Pool(100)

from utils import *
from modules import *

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


def run_fofas(fofatype, fofaquerys,fofadata:FofaData):
    for q in fofaquerys:
        code = getfofaquery(fofatype,q)
        data = get_fofa(code)

        ips, urls, domains, icps = sort_fofadata(data)
        fofadata.union_fofa(ips, urls, domains, icps)
    return fofadata


def run(code):
    # todo: 重构,改成递归形式
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
    ips,icos,icps,urls,domains,cidrs = fofadata.getdata().values()
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
# @click.option("--code","-c",help="fofa查询语句",prompt="input fofa query""")
@click.option("--filename","-f",help="输出文件名")
@click.option("--output","-o",default="ip,domain,cidr")
def command(filename,output):
    main(filename,output,FofaData())


def command_again():
    pass

def main(filename,output,fofadata):
    if filename:
        outfunc = partial(write2file, filename=filename)
    else:
        outfunc = print
    while (fofacode := click.prompt("input fofa query")) != "exit":
        tmpfd = run(fofacode)
        tmpfd.outputdata(output.split(","),outfunc=outfunc)

        while out := click.prompt("choice output(ip,cidr,ico,icp,url,domain) or enter [help], [c|continue], [exit], [diff], [merge]"):
            if out == "exit":
                exit()
            elif out in ["continue","c"]: # 如果输入continue,则爬下一条fofa语句
                break
            elif out == "diff":
                (tmpfd-fofadata).outputdata(outfunc=outfunc)
            elif out == "merge":
                fofadata.merge(tmpfd)
            else:
                fofadata.outputdata(outfunc=print)


if __name__ == '__main__':
    command()
