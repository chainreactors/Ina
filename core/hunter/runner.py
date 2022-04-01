from operator import itemgetter
import vthread

from .. import logging
from ..runner import Runner
from .client import HunterClient


class HunterRunner(Runner):
    name = "hunter"

    def __init__(self):
        self.client = HunterClient()
        self.cache = {}

    def run_code(self, codestr):
        logging.info(f"{self.name} querying {codestr}")
        return self.client.query(codestr)

    @vthread.pool(1, "ina"+name)
    def async_run_code(self, code):
        self.cache[code.to_string(self.name)] = self.run_code(code.to_string(self.name))

    def data_format(self, data):
        need_keys = {
            "ip": "ip",
            "domain": "domain",
            "url": "url",
            "icp": "number",
        }
        return dict(zip(need_keys.keys(), zip(*[itemgetter(*need_keys.values())(i) for i in data])))


