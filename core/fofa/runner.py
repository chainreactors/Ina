import vthread

from .. import logging
from ..runner import Runner
from .client import FofaClient


class FofaRunner(Runner):
    name = "fofa"

    def __init__(self):
        self.client = FofaClient()
        self.cache = {}

    def run_code(self, codestr):
        logging.info(f"{self.name} querying {codestr}")
        return self.client.query(codestr, isfilter=True)

    @vthread.pool(1, "ina"+name)
    def async_run_code(self, code):
        self.cache[code.to_string(self.name)] = self.run_code(code.to_string(self.name))

    def data_format(self, data):
        keys = ["url", "ip", "port", "domain", "title", "icp"]
        return [dict(zip(keys, d)) for d in data]






