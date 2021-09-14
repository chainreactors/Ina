import gevent
from queue import Queue
from gevent.pool import Pool

from .util import *
from .fofadata import FofaData
from .Depth import *
from webtookit import *


class Fofa:
    def __init__(self, client, thread=100):
        self.client = client
        self.taskqueue = Queue()
        self.querys = set()
        self.g = Pool(thread)
        self.fd = FofaData()

    def get_fofa(self,code):
        if code not in self.querys and code != "":
            logging.info("fofa querying " + code)
            self.querys.add(code)
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
            data = self.get_fofa(args[0])
        elif len(args) > 1:
            key, targets = args
            code = join_fofaqueries(**{key: targets})
            data = self.get_fofa(code)
        else:
            return
        urls, ips, domains, icps, ok = self.combine_fofa_result(fd, data)  # 合并数据,返回新增的数据
        if not ok:  # 如果fofa无数据,则退出
            return

        # 获取ico,将得到的ico_hash加入到队列
        self.enqueue("icon_hash", self.callback_ico(urls, fd), depth + 1)

        _, domains_icp = self.callback_icp(icps, fd)  # 通过icp获取ip与domain
        diffdomains = domains.union(domains_icp)
        self.enqueue("domain", diffdomains, depth + 1)  # 将domains以domain加入到队列 # 将domains以cert加入到队列
        self.enqueue("cert", diffdomains, depth + 1)

    def run(self,code):
        tmpfd = self.copy_fd()
        self.run_fofa(code, fd=tmpfd)
        while self.taskqueue.qsize() > 0:
            k, targets, depth = self.taskqueue.get()
            if targets:
                self.run_fofa(k, targets, fd=tmpfd, depth=depth)

        return tmpfd

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

    def filter_icp(self,jobs):
        if jobs == None:
            return []
        res = []
        for domains in getvalues(jobs):
            res += [i for i in domains.keys() if not is_contains_chinese(i)]
        return res

    def callback_icp(self,icps, fd):
        icpjobs = [self.g.spawn(Beian.get_host, icp) for icp in icps]
        gevent.joinall(icpjobs)
        ips, domains = sort_doaminandip(self.filter_icp(icpjobs))
        return fd.unions(ip=ips, domain=domains)
