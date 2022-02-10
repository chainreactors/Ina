import logging
import vthread

from .code import Code
from .client import Client


class Runner:
    name: str
    codes: Code
    cache: dict
    client: Client

    def run_code(self, code):
        if code := self.codes.get_code_from_diff_and_union(code):
            logging.info(f"{self.name} querying {code}")
            return self.client.query(code, isfilter=True)
        else:
            return []

    @vthread.pool(1, name)
    def async_run_code(self, code):
        self.cache[str(code)] = self.run_code(code)
