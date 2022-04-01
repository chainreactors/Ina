from collections import Counter


class Pair:
    link_symbol = {
        "fofa": "=",
        "zoomeye": ":",
        "hunter": ":"
    }

    default_key = {
        "ico": "ico",
        "icp": "icp",
        "cert": "cert",
        "domain": "domain",
        "ip": "ip",
        "cidr": "cidr",
    }

    fofa_key = {
        "ico": "icon_hash",
        "cidr": "ip"
    }

    hunter_key = {
        "ico": "web.icon",
        "cidr": "ip"
    }

    zoomeye_key = {
        "cert": "ssl",
        "domain": "hostname",
        "ico": "iconhash",
        "icp": "-"
    }

    def __init__(self, k, v, source):
        self.update_type(source)
        self.key = k
        self.value = v

    def __hash__(self):
        return hash(self.key + self.value)

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    # def __str__(self):
    #     return f'{self.key_map()}{self.symbol}"{self.value}"'

    def update_type(self, source):
        self.source = source
        self.symbol = self.link_symbol[source]

    def map_key(self, typ):
        return getattr(self, f"{typ}_key", self.default_key).get(self.key, self.default_key[self.key])

    def to_string(self, typ=None):
        # self.update_type(typ)
        if not typ:
            typ = self.source
        if self.map_key(typ) == "-":
            return self.value
        return f'{self.map_key(typ)}{self.link_symbol[typ]}"{self.value}"'


class Code:
    or_symbol = {
        "fofa": "||",
        "zoomeye": " ",
        "hunter": "or"
    }

    def __init__(self, source="fofa", code=None, **kwargs):
        self.params = set()
        self.update_type(source)

        if code:
            self.params = self.split(code.strip())
            return
        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, str):
                    self.params.add(self.pair(k, v))
                elif isinstance(v, (list, set)):
                    [self.params.add(self.pair(k, i)) for i in v]
            return

    def __len__(self):
        len(self.params)

    def __contains__(self, item):
        return item.params < self.params

    def __sub__(self, other):
        fc = Code(other.source)
        fc.params = self.params - other.params
        return fc

    def __add__(self, other):
        fc = Code(other.source)
        fc.params = self.params.union(other.params)
        return fc

    def major_type(self):
        return Counter([p.key for p in self.params]).most_common()[0][0]

    def pair(self, k, v):
        return Pair(k, v, self.source)

    def union(self, other):
        self.params = self.params.union(other.params)
        return self.join()

    def get_diff_code_and_union(self, fc):
        tmpcode = fc - self
        self.union(fc)
        return tmpcode

    def update_type(self, source):
        self.source = source
        self.symbol = self.or_symbol[source]

    def splice(self, key, value):
        if value:
            return f'{key}{self.symbol}"{value}"'
        else:
            return ""

    def split(self, s):
        link_symbol = Pair.link_symbol[self.source]
        return {self.pair(c.split(link_symbol)[0], c.split(link_symbol)[1].strip('"')) for c in s.split(f" {self.symbol}")}

    def join(self, typ=None):
        if typ:
            symbol = self.or_symbol[typ]
        else:
            symbol = self.symbol
        return f" {symbol} ".join([pair.to_string(typ) for pair in self.params])

    def short(self):
        return self.to_string()[:15]

    def to_string(self, typ=None):
        return self.join(typ)
