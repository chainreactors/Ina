import logging, gevent
from queue import Queue
import vthread

from ..util import *
from ..code import Code
from ..depth import CheckDepth
from .fofaclient import FofaClient
from webtookit import Beian_TYC, sort_doaminandip, get_hash, get_icp
from settings import cidrcollect, recu_ico


class FofaRunner:
    name = "fofa"

    def __init__(self):
        self.client = FofaClient()
        self.taskqueue = Queue()
        self.codes = Code(self.name)
        self.cache = {}

    def run_code(self, code):
        if code := self.codes.get_code_from_diff_and_union(code):
            logging.info(f"{self.name} querying {code}")
            return self.client.query(code, isfilter=True)
        else:
            return []

    @vthread.pool(1, name)
    def async_run_code(self, code):
        self.cache[str(code)] = self.run_code(code)

    def get(self, code):
        return self.cache[str(code)]
    # def get_fofa(self, fc):
    #     if code := self.fc.diffunion(fc):
    #         logging.info("fofa querying " + code)
    #         return self.client.query(code, isfilter=True)
    #     else:
    #         return []

    # def cset(self,iter):
    #     "unique and remove blank elem"
    #     s = set(iter)
    #     if "" in iter:
    #         s.remove("")
    #     return s

    def combine_and_diff(self, data):
        """
        :param data:
        :return : different urls,ips,domains,icps,bool
        :rtype : List[set],bool
        """
        if len(data) == 0:
            return {}, {}, {}, {}, False
        keys = ["url", "ip", "", "domain", "", "icp"]
        return *[self.fd.union(keys[i], self.cset(v)) for i, v in enumerate(zip(*data)) if i != 2 and i != 4], True

    # def check_fofatype(self,fofatype):
    #     if isinstance(fofatype, list) or isinstance(fofatype, tuple):
    #         for t in fofatype:
    #             assert t in ["cert", "domain", "ip", "icon_hash", "cidr"], "%s fofa query type"
    #     assert fofatype in ["cert", "domain", "ip", "icon_hash", "cidr"], "%s fofa query type"
    #     return True

    # @CheckDepth
    # def run_fofa(self, fc, depth):
    #     data = self.get_fofa(fc)
    #
    #     urls, ips, domains, icps, ok = self.combine_and_diff(data)  # 合并数据,返回新增的数据
    #     if not ok:  # 如果fofa无数据,则退出
    #         return
    #
    #     # 获取ico,将得到的ico_hash加入到队列
    #     if depth < recu_ico:
    #         self.enqueue("icon_hash", self.collect_ico(urls), depth+1)
    #
    #     if depth < recu_ico:
    #         self.enqueue("icp", self.collect_icp(urls), depth+1)
    #     _, domains_icp = self.callback_icp(icps)  # 通过icp获取ip与domain
    #     diffdomains = domains.union(domains_icp)
    #     self.enqueue("domain", diffdomains, depth + 1)  # 将domains以domain加入到队列 # 将domains以cert加入到队列
    #     self.enqueue("cert", diffdomains, depth + 1)

    # def copy_fd(self):
    #     tmpfd = FofaData(False)
    #     tmpfd.merge(self.fd)
    #     tmpfd.printdiff = True
    #     tmpfd.printfunc = logging.info
    #     return tmpfd

    # def collect_ico(self, urls):
    #     icojobs = [self.g.spawn(get_hash, url) for url in urls]
    #     gevent.joinall(icojobs)
    #     icos = self.filter_ico(icojobs)
    #     return self.fd.union("ico", icos)
    #
    # def collect_icp(self, urls):
    #     icpjobs = [self.g.spawn(get_icp, url) for url in urls]
    #     gevent.joinall(icpjobs)
    #     icps = self.filter_icp(icpjobs)
    #     return self.fd.union("icp", icps)
    #
    # def filter_icp(self,jobs):
    #     # 从gevent jobs中滤出有效icp
    #     if jobs == None:
    #         return []
    #     res = []
    #     for domains in getvalues(jobs):
    #         res += [i for i in domains.keys() if not is_contains_chinese(i)]
    #     return res
    #
    # def filter_ico(self, jobs):
    #     # 从gevent jobs中滤出有效ico_hash
    #     if jobs == None:
    #         return []
    #     icohashs = [str(i[0]) for i in getvalues(jobs) if i[0] and not i[1]]
    #     return [k for k, v in Counter(icohashs).items() if v >= 3]
    #
    # def filter_domains(self,domains):
    #     return [domain for domain in domains if not is_contains_chinese(domain)]
    #
    # def callback_icp(self,icps):
    #     logging.info("requests for %s"%icps)
    #     res = []
    #     for icp in icps:
    #         res += self.beian.get_domain_from_icp(icp)
    #     ips, domains = sort_doaminandip(self.filter_domains(res))
    #     return self.fd.unions(ip=ips, domain=domains)

    # def run(self, fc):
    #     self.run_fofa(fc)
    #     while self.taskqueue.qsize() > 0:
    #         fc, depth = self.taskqueue.get()
    #         self.run_fofa(fc, depth=depth)
    #
    #     if not cidrcollect:
    #         return self.fd
    #     else:
    #         # 递归结束后,收集已知cidr的资产
    #         for cidr in filter(lambda x:x.split("/")[1] != "32", self.fd.update_cidr()):
    #             logging.info("collect cidr assets %s"%cidr)
    #             data = self.get_fofa(FofaCode(ip=cidr))
    #             self.combine_and_diff(data)
    #         return self.fd



