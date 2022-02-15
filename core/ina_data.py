from .util import *


class InaData:
    types = ["ico", "ip", "icp", "url", "domain", "cidr"]

    def __init__(self, printdiff=False, printfunc=print):
        for t in self.types:
            self[t] = set()
        self.print_diff = printdiff
        self.printer = printfunc
        # self.cache = cache

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        self.__dict__[self.getkey(key)] = set(value)

    def __getattr__(self, item):
        return self.__dict__[self.getkey(item)]

    def __sub__(self, other):
        # 获得数据差
        res = InaData()
        for t in self.types:
            res[t] = self[t] - other[t]
        return res

    def getkey(self,k):
        # 判断目标数据是否合法
        assert k in self.types,"%s type not found" % k
        return k

    def __format_icp(self, icps):
        # 格式化icp
        return {icp.split("-")[0] for icp in icps}

    def __format_ipv4(self, ips):
        # 去除ipv6地址
        return {ip for ip in ips if is_ipv4(ip)}

    def update_cidr(self):
        # 因为目前不能做到cidr动态更新, 因此在特定阶段手动调用
        cidr = guessCIDRs(self["ip"])
        self["cidr"] = cidr
        return cidr

    def union(self, t, data):
        # 去重合并数据,并且返回新增的数据
        if not data or not (data := [d for d in data if d]):
            return []
        data = set(data)
        if t == "icp": # icp格式化
            data = self.__format_icp(data)
        elif t == "ip":
            data = self.__format_ipv4(data)
        elif t == "cidr":
            return self.update_cidr()

        diff = self.diff(t, data)
        if self.print_diff:
            if len(diff) != 0:
                self.printer("add %d new %s %s" % (len(diff), t, str(diff)))
        self[t] = self[t].union(data)
        return diff

    def unions(self, **kwargs):
        # 批量更新数据
        return [self.union(k, v) for k, v in kwargs.items()]

    def diff(self, t, data):
        # 获得指定类型相差的数据
        if t == "icp": # icp格式化
            data = self.__format_icp(data)
        return set(data) - self[t]

    def diffs(self,**kwargs):
        return [self.diff(k,v) for k,v in kwargs.items()]

    def merge(self, other):
        # 合并ina_data
        return {t: self.union(t, other[t]) for t in self.types}

    def output(self, types=["ip", "cidr", "domain"], outfunc=print):
        # 输出
        self.update_cidr()
        if types == "all":
            types = self.types

        for t in types:
            if self.getkey(t) and self[t]:
                outfunc("\n".join(self[t])+"\n")

    def to_dict(self):
        self.update_cidr()
        return {t: self[t] for t in self.types}