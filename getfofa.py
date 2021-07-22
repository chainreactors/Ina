import click
from vthread import pool,thread
from queue import Queue
from time import sleep

from fofaclient import FofaClient
from iputil import *
from favicon import get_hash
from icp import Beian,get_icp

class GetFofa:
    def __init__(self):
        self.client = FofaClient()
        self.taskqueue = Queue()
        self.dataqueue = Queue()
        self.icocounter = Counter()

        self.domains = []
        self.ips = []
        self.icps = []
        self.urls = []
        self.printedips = []
        self.printeddomains = []

    @pool(20,gqueue="ico")
    def multi_getfaviconhash(self,url):
        hash,name = get_hash(url,"mmh3")
        if not name and hash:
            self.icocounter.update([hash])
            if self.icocounter[hash] == 3:
                self.taskqueue.put((hash,"ico"))

    @pool(20,gqueue="icp")
    def multi_gethostbyicp(self,icp):
        for host in Beian.get_host(icp):
            if host not in self.domains:
                self.domains.append(host)
                self.taskqueue.put((host,"cert"))

    @pool(20)
    def multi_geticp(self,url):
        if url not in self.urls:
            self.urls.append(url)
            icp = get_icp(url)
            if icp and icp not in self.icps:
                self.multi_gethostbyicp(icp)

    def query_cert(self,domain):
        return self.client.query(f'cert="{domain}"')

    def query_ico(self,hash):
        return self.client.query(f'icon_hash="{hash}"')

    def query_icp(self,icp):
        return self.client.query(f'body="{icp}"')

    def query(self,code):
        return self.client.query(code)

    @pool(20,gqueue="fofa")
    def multi_fofa(self,t,source=None):
        print(t,source)
        if source == "cert":
            data = self.query_cert(t)
        elif source == "icp":
            data = self.query_icp(t)
        elif source == "ico":
            data = self.query_ico(t)
        else:
            data = self.query(t)

        if data:
            self.dataqueue.put(data)

    @pool(1,gqueue="main")
    def fofa_main(self):
        while True:
            # print(self.taskqueue.qsize())
            for _ in range(self.taskqueue.qsize()):
                t,source = self.taskqueue.get()
                print(f"run fofa query from {source}:{t}")
                self.multi_fofa(t,source)
                sleep(1)


    @pool(1,gqueue="data")
    def data_handler(self):
        while True:
            for _ in range(self.dataqueue.qsize()):
                data = self.dataqueue.get()
                self.add_task(data)
                self.print_log(data)
                sleep(1)

    def sort_data(self,data):
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


    def add_task(self,data):
        ips, urls, domains, icps = self.sort_data(data)
        for icp in icps:
            icp = icp.split("-")[0]
            if icp not in self.icps:
                self.icps.append(icp)
                self.multi_gethostbyicp(icp)
            # self.multi_fofa(icp,"icp")

        [self.multi_getfaviconhash(url) for url in urls]



    def print_log(self,data,need=["domain","ip"]):
        # data = list(map(lambda x:dict(zip(("url", "ip", "port", "domain", "title", "icp"),x)),data))
        for d in data:
            if d[1] and d[1] not in self.printedips:
                self.printedips.append(d[1])
                print(d[1])
            if d[3] and d[3] not in self.printeddomains:
                self.printeddomains.append(d[3])
                print(d[3])




    def run(self,code):
        self.data_handler()
        self.fofa_main()
        self.multi_fofa(code)




if __name__ == '__main__':
    # c = FofaClient()
    # res = spider(c,"mca.gov.cn")
    gf = GetFofa()
    gf.run('cert="mca.gov.cn"')
    # print(gf.multi_geticp())
