import logging,gevent
from queue import Queue
from gevent.pool import Pool

from .util import *
from .fofadata import FofaData
from .fofacode import FofaCode
from .depth import *
from webtookit import *
from settings import cidrcollect


class Fofa:
    def __init__(self, thread=100):
        self.beian = Beian_TYC()
        self.client = FofaClient()
        self.taskqueue = Queue()
        self.g = Pool(thread)
        self.fd = FofaData()
        self.fc = FofaCode()

    def get_fofa(self, fc):
        if code := self.fc.diffunion(fc):
            logging.info("fofa querying " + code)
            return self.client.query(code, isfilter=True)
        else:
            return []

    def cset(self,iter):
        "remove blank elem"
        s = set(iter)
        if "" in iter:
            s.remove("")
        return s

    def combine_fofa_result(self, fd: FofaData, data):
        """
        :param data:
        :return : different urls,ips,domains,icps,bool
        :rtype : List[set],bool
        """
        if len(data) == 0:
            return {}, {}, {}, {}, False
        keys = ["url", "ip", "", "domain", "", "icp"]
        return *[fd.union(keys[i], self.cset(v)) for i, v in enumerate(zip(*data)) if i != 2 and i != 4], True

    def check_fofatype(self,fofatype):
        if isinstance(fofatype, list) or isinstance(fofatype, tuple):
            for t in fofatype:
                assert t in ["cert", "domain", "ip", "icon_hash", "cidr"], "%s fofa query type"
        assert fofatype in ["cert", "domain", "ip", "icon_hash", "cidr"], "%s fofa query type"
        return True

    def enqueue(self,k, targets, depth):
        self.taskqueue.put((k, targets, depth))

    @CheckDepth
    def run_fofa(self, *args, fd: FofaData, depth):
        if len(args) == 1:
            data = self.get_fofa(FofaCode(args[0]))
        elif len(args) > 1:
            key, targets = args
            data = self.get_fofa(FofaCode(**{key: targets}))
        else:
            return

        urls, ips, domains, icps, ok = self.combine_fofa_result(fd, data)  # 合并数据,返回新增的数据
        if not ok:  # 如果fofa无数据,则退出
            return

        # 获取ico,将得到的ico_hash加入到队列
        if depth < recu_ico:
            self.enqueue("icon_hash", self.callback_ico(urls, fd), depth + 1)

        _, domains_icp = self.callback_icp(icps, fd)  # 通过icp获取ip与domain
        diffdomains = domains.union(domains_icp)
        self.enqueue("domain", diffdomains, depth + 1)  # 将domains以domain加入到队列 # 将domains以cert加入到队列
        self.enqueue("cert", diffdomains, depth + 1)

    def run(self,code):
        fd = self.copy_fd()
        self.run_fofa(code, fd=fd)
        while self.taskqueue.qsize() > 0:
            k, targets, depth = self.taskqueue.get()
            if targets:
                self.run_fofa(k, targets, fd=fd, depth=depth)

        # 爬虫结束后,收集所有的ip与端口
        if not cidrcollect:
            return fd

        for cidr in filter(lambda x:x.split("/")[1] != "32", fd.update_cidr()):
            logging.info("collect cidr assets %s"%cidr)
            data = self.get_fofa(FofaCode(ip=cidr))
            self.combine_fofa_result(fd, data)

        return fd

    def copy_fd(self):
        tmpfd = FofaData(False)
        tmpfd.merge(self.fd)
        tmpfd.printdiff = True
        tmpfd.printfunc = logging.info
        return tmpfd

    def callback_ico(self,urls, fd):
        icojobs = [self.g.spawn(get_hash, url) for url in urls]
        gevent.joinall(icojobs)
        icos = filter_ico(icojobs)
        return fd.union("ico",icos)

    # def filter_icp(self,jobs):
    #     if jobs == None:
    #         return []
    #     res = []
    #     for domains in getvalues(jobs):
    #         res += [i for i in domains.keys() if not is_contains_chinese(i)]
    #     return res
    def filter_domains(self,domains):
        return [domain for domain in domains if not is_contains_chinese(domain)]

    def callback_icp(self,icps, fd):
        res = []
        for icp in icps:
            res += self.beian.get_domain_from_icp(icp)
        ips, domains = sort_doaminandip(self.filter_domains(res))
        return fd.unions(ip=ips, domain=domains)

