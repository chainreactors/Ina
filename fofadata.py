class FofaData:
    def __init__(self,printdiff=False,printfunc=print):
        self.printdiff = printdiff
        self.printfunc = printfunc

    def __getitem__(self, item):
        return getattr(self,item)

    def __setitem__(self, key, value):
        key = self.getkey(key)
        self.__dict__[key] = value

    def __getattr__(self, item:str):
        item = self.getkey(item)
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            self.__dict__[item] = set()
            return self.__dict__[item]

    def getkey(self,k):
        assert k in ["ipset","icpset","urlset","domainset","icoset","ico","ip","icp","url","domain","cidr"],"data type not found"
        if not k.endswith("set"):
            k += "set"
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

    def getdata(self, types=None):
        if types is None:
            types = ["ip", "icp","ico", "url", "domain"]
        return [self[t] for t in types]

