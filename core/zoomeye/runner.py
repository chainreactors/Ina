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

    def data_format(self, data):
        res = {k: [] for k in ["ip", "domain", "url", "ico"]}
        for d in data:
            res["domain"].append(d.get("rdns", "").lower())
            res["ip"].append(d["ip"])
            res["ico"].append(d.get("ico",{}).get("mmh3", ""))
            res["url"].append(f"{d['portinfo']['service']}://{d['ip']}:{d['portinfo']['port']}")
        return res
