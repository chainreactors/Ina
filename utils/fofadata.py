from utils.iputil import guessCIDRs
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

    def __getattr__(self, item:str):
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

    def union(self,t,data):
        if t == "icp": # icp格式化
            data = [icp.split("-")[0] for icp in data]
        diff = set(data) - self[t]
        if self.printdiff:
            if len(diff) != 0:
                self.printfunc("add %d new %s %s"%(len(diff),t,str(diff)))
        self[t] = self[t].union(set(data))
        return diff

    def unions(self,**kwargs):
        diffs = []
        for k,v in kwargs.items():
            diffs.append(self.union(k,v))
        return diffs

    def union_fofa(self,ips,urls,domains,icps):
        self.union("ip",ips)
        self.union("url",urls)
        self.union("domain",domains)
        self.union("icp",icps)

    def merge(self, other):
        for t in self.types:
            if t == "cidr":
                self["cidr"] = guessCIDRs(self["ip"])
            else:
                self.union(t,other[t])

    def initialize(self):
        for t in self.types:
            self[t] = set()

    def getdata(self, types=None):
        if types is None:
            types = self.types
        return {t:self[t] for t in types}

    def outputdata(self,types=["ip","cidr","domain"], outfunc=print):
        for t in types:
            if self.check_type(t) and len(self[t]):
                outfunc("\n".join(self[t])+"\n")




if __name__ == '__main__':
    f1 = FofaData()
    f2 = FofaData()
    f1["ip"] = {"1.1.1.1","2.2.2.2"}
    f2["ip"] = {"2.2.2.2"}
    res = f1-f2
    print(res)