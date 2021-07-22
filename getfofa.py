from fofaclient import FofaClient
from iputil import *


def spider(c,domain):
    return c.query(f'cert="{domain}"')

if __name__ == '__main__':
    c = FofaClient()
    res = spider(c,"mca.gov.cn")
    for i in set(map(lambda x: x[3], res)):
        print(i)
    # for i in set():
    #     print(i)
    for i in statCIDR(map(lambda x: x[1], res)).values():
        print(guessCIDR(i))
