import vthread

from .. import logging
from ..runner import Runner
from .client import ZoomeyeClient


class ZoomeyeRunner(Runner):
    name = "zoomeye"

    def __init__(self):
        self.client = ZoomeyeClient()
        self.cache = {}

    def run_code(self, codestr):
        logging.info(f"{self.name} querying {codestr}")
        return self.client.query(codestr)

    @vthread.pool(1, "ina"+name)
    def async_run_code(self, code):
        self.cache[code.to_string(self.name)] = self.run_code(code.to_string(self.name))

    def extract_data(self, d):
        return {
            "ip": d["ip"],
            "port": d["port"],
            "domain": d.get("rdns", "").lower(),
            "ico": d.get("ico", {}).get("mmh3", ""),
            "url": f"{d['portinfo']['service']}://{d['ip']}:{d['portinfo']['port']}",
        }

    def data_format(self, data):
        return [self.extract_data(d) for d in data]
