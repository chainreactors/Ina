import vthread

from .. import logging, InaData
from ..ina_code import Code
from ..runner import Runner
from .zoomeyeclient import ZoomeyeClient


class ZoomeyeRunner(Runner):
    name = "zoomeye"

    def __init__(self):
        self.client = ZoomeyeClient()
        self.codes = Code(self.name)
        self.cache = {}

    def run_code(self, codestr):
        logging.info(f"{self.name} querying {codestr}")
        return self.client.query(codestr)

    @vthread.pool(1, "ina" + name)
    def async_run_code(self, code):
        self.cache[code.to_string(self.name)] = self.run_code(code.to_string(self.name))

    def get(self, code):
        return self.cache.get(code.to_string(self.name), None)

    def to_idata_from_cache(self, code):
        if not (data := self.get(code)):
            return None
        return self.to_idata(data)

    def to_idata(self, data):
        if not data:
            return None

        keys = ["url", "ip", "", "domain", "", "icp"]
        idata = InaData()
        idata.unions(**{keys[i]: v for i, v in enumerate(zip(*data)) if keys[i]})
        return idata
