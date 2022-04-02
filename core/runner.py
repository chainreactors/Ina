import logging

from .client import Client
from .ina_data import InaData


class Runner:
    # 定义runner所需的基本接口
    name: str
    cache: dict
    client: Client

    def get(self, code):
        return self.cache.get(code.to_string(self.name), None)

    def get_idata_from_cache(self, code):
        if not (data := self.get(code)):
            return None
        return self.to_idata(data)

    def run_code(self, codestr):
        logging.info(f"{self.name} querying {codestr}")
        return self.client.query(codestr)

    def data_format(self, data) -> dict:
        pass

    def to_idata(self, data):
        if not data:
            return None

        idata = InaData()
        idata.union(self.data_format(data))
        return idata
