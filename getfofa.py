import logging

import click
import gevent
import vthread
from gevent import monkey
from gevent.pool import Pool
from functools import partial
from queue import Queue
from vthread import pool

monkey.patch_all()
g = Pool(100)

from utils import *
from webtookit import *


client = FofaClient()
taskqueue = Queue()
fd = FofaData(True, logging.info)
querys = set()


def get_fofa(code):
    if code not in querys and code != "":
        logging.info("fofa querying "+code)
        querys.add(code)
        return client.query(code,isfilter=True)
    else:
        return []


def combine_fofa_result(fd:FofaData, data):
    """
    :param data:
    :return : different urls,ips,domains,icps,bool
    :rtype : List[set],bool
    """
    if len(data) == 0:
        return {},{},{},{},False
    keys = ["url", "ip", "", "domain", "", "icp"]
    return *[fd.union(keys[i],set(v)) for i,v in enumerate(zip(*data)) if i !=2 and i != 4],True


def getfofaquery(fofatype,fofaquery):
    assert fofatype in ["cert","domain","ip","icon_hash"] ,"error fofa query type"
    if fofaquery == "":
        return ""
    return f'{fofatype}="{fofaquery}"'


def run_fofas(fofatype, fofaquerys):
    for q in fofaquerys:
        code = getfofaquery(fofatype,q)
        data = get_fofa(code)
        combine_fofa_result(fd, data)
        # fofadata.union_fofa(ips, urls, domains, icps)

def enqueue(k,data,depth):
    for d in data:
        taskqueue.put((getfofaquery(k,d),depth))

@CheckDepth
def run_fofa(code,depth=1):
    data = get_fofa(code)
    urls, ips, domains, icps, ok = combine_fofa_result(fd, data) # 合并数据,返回新增的数据
    if not ok: # 如果fofa无数据,则退出
        return
    enqueue("ico",callback_ico(urls),depth+1) # 获取ico,将得到的ico_hash加入到队列
    _, domains_icp = callback_icp(icps) # 通过icp获取ip与domain
    domains.union(domains_icp)
    enqueue("domain",domains,depth+1)  # 将domains以domain加入到队列
    enqueue("cert",domains,depth+1) # 将domains以cert加入到队列


def run(code):
    run_fofa(code)
    while taskqueue.qsize() > 0:
        run_fofa(*taskqueue.get())


def callback_ico(urls):
    icojobs = [g.spawn(get_hash,url) for url in urls]
    gevent.joinall(icojobs)
    return filter_ico(icojobs)


def callback_icp(icps):
    icpjobs = [g.spawn(Beian.get_host, icp) for icp in icps]
    gevent.joinall(icpjobs)
    ips,domains = sort_doaminandip(filter_icp(icpjobs))
    fd.unions(ip=ips, domain=domains)
    return ips,domains


@click.command()
# @click.option("--code","-c",help="fofa查询语句",prompt="input fofa query""")
@click.option("--filename","-f",help="输出文件名")
@click.option("--output","-o",default="ip,domain,cidr")
def command(filename,output):
    main(filename,output,FofaData())



def main(filename,output,fofadata):
    if filename:
        outfunc = partial(write2file, filename=filename)
    else:
        outfunc = print
    while (fofacode := click.prompt("input fofa query")) != "exit":
        run(fofacode)
        tmpfd = fd
        fd.initialize()
        tmpfd.outputdata(output.split(","),outfunc=outfunc)

        while out := click.prompt("choice output(ip,cidr,ico,icp,url,domain) or enter [help], [c|continue], [exit], [diff], [merge], [to_file <filename>]"):
            if out == "exit":
                exit()
            elif out == "":
                continue
            elif out in ["continue","c"]: # 如果输入continue,则爬下一条fofa语句
                break
            elif out == "diff":
                (tmpfd - fofadata).outputdata(outfunc=outfunc)
            elif out == "merge":
                fofadata.merge(tmpfd)
            elif "to_file" in out:
                outs = out.split(" ")
                if len(outs) >= 2 or filename:
                    tmpfilename = filename if filename else outs[-1]
                    printfunc= partial(write2file,filename=tmpfilename)
                    sum = fofadata.outputdata(outfunc=printfunc)
                    if sum:
                        print("maybe no result or not merge")
                else:
                    print("please input filename,example: to_file out.txt")
                    continue
            else:
                fofadata.outputdata(out.split(","),outfunc=print)


if __name__ == '__main__':
    # command()
    command()
    # pool.waitall()
