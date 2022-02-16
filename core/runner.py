import logging
import vthread

from .ina_code import Code
from .client import Client


class Runner:
    # 定义runner所需的基本接口
    name: str
    cache: dict
    client: Client

    def get(self, code):
        code.update_type(self.name)
        return self.cache.get(str(code), None)

    def to_idata_from_cache(self, code):
        if not (data := self.get(code)):
            return None
        return self.to_idata(data)

    def run_code(self, codestr):
        logging.info(f"{self.name} querying {codestr}")
        return self.client.query(codestr)

    def to_idata(self, data):
        pass
