import click
from vthread import pool
from queue import Queue

from fofaclient import FofaClient
from iputil import *
from favicon import get_hash

class GetFofa:
    def __init__(self):
        self.client = FofaClient()
        self.icohashqueue = Queue()
        self.icocounter = Counter()

    @pool(20,gqueue="ico")
    def multi_favicon(self,url):
        hash,name = get_hash(url,"mmh3")
        if not name and hash:
            self.icocounter.update([hash])
            if self.icocounter[hash] == 3:
                self.icohashqueue.put(hash)

    @pool(20,gqueue="icp")
    def multi_icp(self,icp):
        pass

    def query_cert(self,domain):
        return self.client.query(f'cert="{domain}"')

    def query_ico(self,hash):
        return self.client.query(f'icon_hash="{hash}"')

    def query_icp(self,icp):
        return self.client.query(f'body="{icp}"')

    def run_query(self,source,t):
        if source == "cert":
            res = self.query_cert(t)
        elif source == "icp":
            res = self.query_icp(t)
        elif source == "ico":
            res = self.query_icp(t)



if __name__ == '__main__':
    # c = FofaClient()
    # res = spider(c,"mca.gov.cn")
    pass
