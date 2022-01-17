
class Pair:
    link_symbol = {
        "fofa": "=",
        "zoomeye": ":"
    }

    def __init__(self, k, v, typ):
        self.symbol = self.link_symbol[typ]
        self.key = k
        self.value = v

    def __hash__(self):
        return hash(self.key + self.value)

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __str__(self):
        return f'{self.key}{self.symbol}"{self.value}"'


class Code:
    or_symbol = {
        "fofa": "||",
        "zoomeye": " "
    }

    def __init__(self, typ, code=None, **kwargs):
        self.params = set()
        self.typ = typ
        self.symbol = self.or_symbol[typ]

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

    def get_code_from_diff_and_union(self, fc):
        tmpcode = fc - self
        self.union(fc)
        return str(tmpcode)

    def splice(self, key, value):
        if value:
            return f'{key}{self.symbol}"{value}"'
        else:
            return ""

    def split(self, code):
        return {self.pair(c.split(self.symbol)[0], c.split(self.symbol)[1].strip('"')) for c in code.split(f" {self.symbol} ")}

    def join(self, seq):
        return f" {self.symbol} ".join([self.splice(k, v) for k, v in seq])

    def join_from_pairs(self, pairs):
        return f" {self.symbol} ".join([str(pair) for pair in pairs])