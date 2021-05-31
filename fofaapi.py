from . import query
from . import HandleIP


def ProcessFofa(Query):
    raw_dict = query.FofaQuery(Query)
    ip_org_list = list()
    host_list = list()

    for info in raw_dict:
        ip_org_list.append([info[1], info[2]])
        if HandleIP.IPorDoamin(info[0]):
            continue
        else:
            if info[0] != "":
                host = HandleIP.HandleHost(info[0])
                host_list.append(host)
    ip = []

    for info in ip_org_list:
        ip.append(info[0])

    ip = set(list(ip))
    def f(x):
        org = ""
        for i in ip_org_list:
            if i[0] == x:
                if org == "":
                    org = i[1]
                else:
                    break
        return [x, org]

    ip_org_list = list(map(f, ip))

    host_list = list(set(host_list))

    return ip_org_list, host_list

if __name__ == '__main__':
    result1, result2 = ProcessFofa("cert=\"{0}\"".format("baidu.com"))
    print(result1)
    print(result2)
