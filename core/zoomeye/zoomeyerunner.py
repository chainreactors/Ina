import logging, gevent
from queue import Queue
import vthread

from ..code import Code
from .zoomeyeclient import ZoomeyeClient


class FofaRunner:
    name = "fofa"

    def __init__(self):
        self.client = ZoomeyeClient()
        self.taskqueue = Queue()
        self.codes = Code(self.name)
        self.cache = {}

    def run_code(self, code):
        if code := self.codes.get_code_from_diff_and_union(code):
            logging.info(f"{self.name} querying {code}")
            return self.client.query(code, isfilter=True)
        else:
            return []

    @vthread.pool(1, name)
    def async_run_code(self, code):
        self.cache[str(code)] = self.run_code(code)

    def get(self, code):
        return self.cache[str(code)]