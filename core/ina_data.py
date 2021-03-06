from tld import get_fld

from .util import *
from . import logging


def parse_root_domain(domain):
    try:
        if "." in domain:
            return get_fld(domain, fix_protocol=True)
        else:
            return ""
    except:
        return ""


def parse_root_icp(icp):
    return "-".join(icp.split('-')[:-1])


class d:
    def __init__(self, **kwargs):
        if "ip" in kwargs and "url" in kwargs:
            self.attr = {
                "ip": kwargs.pop("ip"),
                "port": str(kwargs.pop("port")),
                "url": kwargs.pop("url"),
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
        return hash(self.ip + self.port + self.domain + self.icp)

    def __eq__(self, other):
        return self.ip == other.ip and self.port == other.port and self.domain == other.domain and self.icp == other.icp

    def to_string(self):
        return "\t".join(self.attr.values())

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
            return list({str(value) for asset in self.assets if (value := getattr(asset, item))})

    def __sub__(self, other):
        return InaData(self.assets - other.assets, self.print_diff, self.printer)

    def __len__(self):
        return len(self.assets)

    def __bool__(self):
        if len(self.assets):
            return True
        return False

    @property
    def ip(self):
        return list({asset.ip for asset in self.assets if asset.ip and is_ipv4(asset.ip)})

    @property
    def icp(self):
        return list({parse_root_icp(asset.icp) for asset in self.assets if asset.icp})

    @property
    def top_domain(self):
        return list({parse_root_domain(asset.domain) for asset in self.assets if asset.domain})

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
        # ??????????????????,???????????????????????????
        diff = self.diff(data)
        self.assets.update(diff)
        return diff

    def merge(self, other):
        # ??????ina_data
        diff = other - self
        if self.print_diff and len(diff):
            self.printer("add %d new assets" % len(diff))
        self.assets.update(other.assets)
        return diff

    def output(self, types=["ip", "cidr", "domain"], printer=None):
        # ??????
        if printer is None:
            printer = self.printer
        if types == "all":
            types = self.types

        for t in types:
            if t in self.types:
                printer("\n".join(self.get(t)))
            else:
                logging.warning("unexpected key: %s, please input : %s" %(t, ", ".join(self.types)))

    def to_dict(self):
        return [asset.to_dict() for asset in self.assets]
