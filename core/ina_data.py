from tld import get_fld

from .util import *


class d:

    def __init__(self, **kwargs):
        if "ip" in kwargs and "url" in kwargs:
            self.attr = {
                "ip": kwargs["ip"],
                "url": kwargs["url"],
            }
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        if key == "attr":
            self.__dict__[key] = value
        else:
            self.attr[key] = value

    def __getattr__(self, item):
        if item in self.attr:
            return self.attr[item]
        return ""

    def __str__(self):
        return self.url

    def __hash__(self):
        return hash(self.url + self.ip + self.icp)

    def __eq__(self, other):
        return self.url == other.url and self.ip == self.ip and self.icp == self.icp

    def to_dict(self):
        return self.attr


class InaData:
    types = ["ip", "domain", "url", "ico", "icp", "cidr", "title"]

    def __init__(self, assets=set(), printdiff=False, printfunc=print):
        if isinstance(assets, set):
            self.assets = assets.copy()
        elif isinstance(assets, list):
            self.assets = {d(**asset) for asset in assets}
        else:
            raise ValueError("unexpect asset type " + str(type(assets)))

        self.print_diff = printdiff
        self.printer = printfunc

    def __getattr__(self, item):
        if item in self.types:
            return list({getattr(asset, item) for asset in self.assets if getattr(asset, item)})

    def __sub__(self, other):
        return InaData(self.assets - other.assets, self.print_diff, self.printer)

    def __len__(self):
        return len(self.assets)

    @property
    def ip(self):
        return list({asset.ip for asset in self.assets if asset.ip and is_ipv4(asset.ip)})

    @property
    def icp(self):
        return list({asset.icp.split("-")[0] for asset in self.assets if asset.icp})

    @property
    def top_domain(self):
        return list({get_fld(asset.domain, fix_protocol=True) for asset in self.assets if asset.domain})

    @property
    def cidr(self):
        return guessCIDRs(self.ip)

    def get(self, key):
        return getattr(self, key)

    def gets(self, keys):
        return [getattr(self, k) for k in keys]

    def diff(self, data):
        return (InaData(data) - self).assets

    def union(self, data):
        # 去重合并数据,并且返回新增的数据
        diff = self.diff(data)
        self.assets.update(diff)
        return diff

    def merge(self, other):
        # 合并ina_data
        diff = other - self
        if self.print_diff and len(diff):
            self.printer("add %d new assets" % len(diff))
        self.assets.update(other.assets)
        return diff

    def output(self, types=["ip", "cidr", "domain"], printer=None):
        # 输出
        if printer is None:
            printer = self.printer
        if types == "all":
            types = self.types

        for t in types:
            printer("\n".join(self.get(t)))

    def to_dict(self):
        return [asset.to_dict() for asset in self.assets]
