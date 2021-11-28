
class FofaPair:
    """
    Fofa查询语句的最小单位,为一对键值对
    """

    def __init__(self,k,v):
        self.key = k
        self.value = v

    def __hash__(self):
        return hash(self.key + self.value)

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __str__(self):
        return f'{self.key}="{self.value}"'


class FofaCode:
    """
    用作记录已经查询过的语句,防止多次重复查询影响效率,也为未来的Cache做准备
    """
    def __init__(self, code=None, **kwargs):
        self.params = set()
        if code:
            self.params = self.split(code.strip())
            return
        if kwargs:
            for k,v in kwargs.items():
                if isinstance(v,str):
                    self.params.add(FofaPair(k,v))
                elif isinstance(v,(list, set)):
                    [self.params.add(FofaPair(k,i)) for i in v]
            return

    def __str__(self):
        return self.joinpairs(self.params)

    def __contains__(self, item):
        return item.params < self.params

    def __sub__(self, other):
        fc = FofaCode()
        fc.params = self.params - other.params
        return fc

    def __add__(self, other):
        fc = FofaCode()
        fc.params = self.params.union(other.params)
        return fc

    def union(self,other):
        self.params = self.params.union(other.params)
        return self.joinpairs(self.params)

    def diff(self, fc):
        return self.joinpairs(fc.params - self.params)

    def diffunion(self, fc):
        diffstr = self.diff(fc)
        self.union(fc)
        return diffstr

    def splice(self, key, value):
        if value:
            return f'{key}="{value}"'
        else:
            return ""

    def split(self, code):
        return {FofaPair(c.split("=")[0], c.split("=")[1].strip('"')) for c in code.split(" || ")}

    def join(self, seq):
        return " || ".join([self.splice(k, v) for k, v in seq])

    def joinpairs(self,pairs):
        return " || ".join([str(pair) for pair in pairs])