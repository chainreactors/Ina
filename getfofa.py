import logging

import click
import gevent
from gevent import monkey
from gevent.pool import Pool
from functools import partial
from queue import Queue

monkey.patch_all()
g = Pool(100)

from utils import *
from webtookit import *


client = FofaClient()
taskqueue = Queue()
querys = set()


def get_fofa(code):
    if code not in querys and code != "":
        logging.info("fofa querying "+code)
        querys.add(code)
        return client.query(code,isfilter=True)
    else:
        return []


def cset(iter):
    "remove blank elem"
    s = set(iter)
    if "" in iter:
        s.remove("")
    return s

def combine_fofa_result(fd:FofaData, data):
    """
    :param data:
    :return : different urls,ips,domains,icps,bool
    :rtype : List[set],bool
    """
    if len(data) == 0:
        return {},{},{},{},False
    keys = ["url", "ip", "", "domain", "", "icp"]
    return *[fd.union(keys[i],cset(v)) for i,v in enumerate(zip(*data)) if i !=2 and i != 4],True


def check_fofatype(fofatype):
    if isinstance(fofatype,list) or isinstance(fofatype,tuple):
        for t in fofatype:
            assert t in ["cert", "domain", "ip", "icon_hash", "cidr"], "%s fofa query type"
    assert fofatype in ["cert", "domain", "ip", "icon_hash", "cidr"], "%s fofa query type"
    return True



# def run_fofas(fofatype, fofaquerys):
#     for q in fofaquerys:
#         code = get_fofaquery(fofatype, q)
#         data = get_fofa(code)
#         combine_fofa_result(fd, data)
        # fofadata.union_fofa(ips, urls, domains, icps)


def enqueue(k, targets, depth):
    taskqueue.put((k,targets,depth))

@CheckDepth
def run_fofa(*args,fd,depth):
    if len(args) == 1:
        data = get_fofa(args[0])
    elif len(args) > 1 :
        key,targets = args
        code = join_fofaqueries(**{key:targets})
        data = get_fofa(code)
    else:
        return
    urls, ips, domains, icps, ok = combine_fofa_result(fd, data) # 合并数据,返回新增的数据
    if not ok: # 如果fofa无数据,则退出
        return

    # 获取ico,将得到的ico_hash加入到队列
    enqueue("icon_hash",callback_ico(urls,fd),depth+1)

    _, domains_icp = callback_icp(icps,fd) # 通过icp获取ip与domain
    domains.union(domains_icp)
    enqueue("domain",domains,depth+1)  # 将domains以domain加入到队列 # 将domains以cert加入到队列
    enqueue("cert",domains,depth+1)

def run(code):
    tmpfd = FofaData(True,logging.info)
    # tmpfd.merge(fd)
    run_fofa(code,fd=tmpfd)
    while taskqueue.qsize() > 0:
        k,targets,depth = taskqueue.get()
        if targets:
            run_fofa(k,targets,fd=tmpfd,depth=depth)

    return tmpfd


def callback_ico(urls,fd):
    icojobs = [g.spawn(get_hash,url) for url in urls]
    gevent.joinall(icojobs)
    icos = filter_ico(icojobs)
    fd.unions(ico=icos)
    return icos


def callback_icp(icps,fd):
    icpjobs = [g.spawn(Beian.get_host, icp) for icp in icps]
    gevent.joinall(icpjobs)
    ips,domains = sort_doaminandip(filter_icp(icpjobs))
    fd.unions(ip=ips, domain=domains)
    return ips,domains


@click.command()
@click.option("--filename","-f",help="输出文件名")
@click.option("--output","-o",default="ip,domain,cidr")
def command(filename,output):
    main(filename,output,FofaData(True))



def main(filename,output,fd:FofaData):
    if filename:
        outfunc = partial(write2file, filename=filename)
    else:
        outfunc = print

    fds = {}
    index = 0
    while (fofacode := click.prompt("input fofa query")) != "exit":
        index += 1
        tmpfd = run(fofacode)
        fds[index] = (fofacode,tmpfd)
        tmpfd.outputdata(output.split(","),outfunc=outfunc)

        while out := click.prompt("choice output(ip,cidr,ico,icp,url,domain) or enter [help], [c|continue], [exit], [diff], [merge], [to_file <filename>]"):
            if out == "exit":
                exit()
            elif out == "":
                continue
            elif out in ["continue","c"]: # 如果输入continue,则爬下一条fofa语句
                break
            elif out == "diff":
                (tmpfd - fd).outputdata(outfunc=outfunc)
            elif "merge" in out:
                if len(v := out.split(" ")) == 1:
                    fd.merge(tmpfd)
                else:
                    fd.merge(fds[v][1])
            elif "to_file" in out:
                outs = out.split(" ")
                if len(outs) >= 2 or filename:
                    tmpfilename = filename if filename else outs[-1]
                    printfunc= partial(write2file,filename=tmpfilename)
                    sum = fd.outputdata(outfunc=printfunc)
                    if sum:
                        print("maybe no result or not merge")
                else:
                    print("please input filename,example: to_file out.txt")
                    continue
            elif out == "help":
                pass
            elif out == "history":
                [print(i,v[0]) for i,v in fds.items()]
            else:
                fd.outputdata(out.split(","),outfunc=print)


if __name__ == '__main__':
    # command()
    command()
    # pool.waitall()
