from webtookit.utils import *


class FofaData:
    types = ["ico","ip","icp","url","domain","cidr"]

    def __init__(self,printdiff=False,printfunc=print):
        self.printdiff = printdiff
        self.printfunc = printfunc

    def __getitem__(self, item):
        return getattr(self,item)

    def __setitem__(self, key, value):
        key = self.getkey(key)
        self.__dict__[key] = set(value)

    def __getattr__(self, item):
        item = self.getkey(item)
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            self.__dict__[item] = set()
            return self.__dict__[item]

    def __sub__(self, other):
        """
        :type other FofaData
        :param other:
        :return:
        """
        res = FofaData()
        for t in self.types:
            res[t] = self[t] - other[t]
        return res

    def getkey(self,k):
        assert k in self.types,"%s type not found"%k
        return k

    def check_type(self,t):
        if t in self.types:
            return True
        else:
            return False

    def _icp(self,icps):
        return {icp.split("-")[0] for icp in icps}

    def _ipv4(self, ips):
        return {ip for ip in ips if is_ipv4(ip)}

    def update_cidr(self):
        cidr = guessCIDRs(self["ip"])
        self["cidr"] = cidr
        return cidr

    def union(self,t,data):
        data = set(data)
        if t == "icp": # icp格式化
            data = self._icp(data)
        elif t == "ip":
            data = self._ipv4(data)
        elif t == "cidr":
            return self.update_cidr()
        diff = data - self[t]
        if self.printdiff:
            if len(diff) != 0:
                self.printfunc("add %d new %s %s"%(len(diff),t,str(diff)))
        self[t] = self[t].union(data)
        return diff

    def unions(self,**kwargs):
        return [self.union(k,v) for k,v in kwargs.items()]

    def diff(self,t,data):
        if t == "icp": # icp格式化
            data = self._icp(data)
        return set(data) - self[t]

    def diffs(self,**kwargs):
        return [self.diff(k,v) for k,v in kwargs.items()]

    def diffs_fd(self,other):
        return [other[t] - self[t] for t in self.types]

    def union_fofa(self,ips,urls,domains,icps):
        self.union("ip",ips)
        self.union("url",urls)
        self.union("domain",domains)
        self.union("icp",icps)

    def merge(self, other):
        for t in self.types:
            self.union(t,other[t])

    def initialize(self):
        for t in self.types:
            self[t] = set()

    def getdata(self, types=None):
        if types is None:
            types = self.types
        return {t:self[t] for t in types}

    def outputdata(self,types=["ip","cidr","domain"], outfunc=print):
        self.update_cidr()
        for t in types:
            if self.check_type(t) and len(self[t]):
                outfunc("\n".join(self[t])+"\n")

    def to_json(self):
        self.update_cidr()
        return {t: self[t] for t in self.types}