class Pair:
    link_symbol = {
        "fofa": "=",
        "zoomeye": ":"
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
    }

    def __init__(self, k, v, typ):
        self.update_type(typ)
        self.key = k
        self.value = v

    def __hash__(self):
        return hash(self.key + self.value)

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __str__(self):
        return f'{self.key_map()}{self.symbol}"{self.value}"'

    def update_type(self, typ):
        self.typ = typ
        self.symbol = self.link_symbol[typ]

    def key_map(self):
        return getattr(self, f"{self.typ}_key", self.default_key).get(self.key, self.default_key[self.key])

    def to_string(self, typ):
        self.update_type(typ)
        return str(self)


class Code:
    or_symbol = {
        "fofa": "||",
        "zoomeye": " "
    }

    def __init__(self, typ="fofa", code=None, **kwargs):
        self.params = set()
        self.update_type(typ)

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

    def __str__(self):
        return self.join_from_pairs(self.params)

    def __len__(self):
        len(self.params)

    def __contains__(self, item):
        return item.params < self.params

    def __sub__(self, other):
        fc = Code(other.typ)
        fc.params = self.params - other.params
        return fc

    def __add__(self, other):
        fc = Code(other.typ)
        fc.params = self.params.union(other.params)
        return fc

    def pair(self, k, v):
        return Pair(k, v, self.typ)

    def union(self, other):
        self.params = self.params.union(other.params)
        return self.join_from_pairs(self.params)

    def get_diff_code_and_union(self, fc):
        tmpcode = fc - self
        self.union(fc)
        return tmpcode

    def update_type(self, typ):
        self.typ = typ
        self.symbol = self.or_symbol[typ]

    def splice(self, key, value):
        if value:
            return f'{key}{self.symbol}"{value}"'
        else:
            return ""

    def split(self, s):
        link_symbol = Pair.link_symbol[self.typ]
        return {self.pair(c.split(link_symbol)[0], c.split(link_symbol)[1].strip('"')) for c in s.split(f" {self.symbol} ")}

    def join(self, seq):
        return f" {self.symbol} ".join([self.splice(k, v) for k, v in seq])

    def join_from_pairs(self, pairs):
        return f" {self.symbol} ".join([str(pair) for pair in pairs])
