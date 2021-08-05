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
        assert k in self.types,"data type not found"
        return k

    def union(self,t,data):
        if t == "icp": # icp格式化
            data = [icp.split("-")[0] for icp in data]

        if self.printdiff:
            diff = set(data) - self[t]
            if len(diff) != 0:
                self.printfunc("add %d new %s %s"%(len(diff),t,str(diff)))

        self[t] = self[t].union(set(data))

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


    def getdata(self, types=None):
        if types is None:
            types = self.types
        return {t:self[t] for t in types}

    def outputdata(self,types=["ip","cidr","domain"], outfunc=print):
        sum = 0
        for t in types:
            if c:=len(self[t]) != 0:
                sum += c
                outfunc("\n".join(self[t])+"\n")
        return sum




if __name__ == '__main__':
    f1 = FofaData()
    f2 = FofaData()
    f1["ip"] = {"1.1.1.1","2.2.2.2"}
    f2["ip"] = {"2.2.2.2"}
    res = f1-f2
    print(res)