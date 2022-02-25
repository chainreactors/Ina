from .ina_data import InaData
from .ina_runner import InaRunner
from .ina_code import Code
from . import logging


class Ina:
    def __init__(self):
        self.idata = InaData(True, logging.info)
        self.codecache = Code()
        self.history = {}

    def input_parser(self, input):
        code = Code(code=input)
        return code

    def run(self, codestr, source="all"):
        runner = InaRunner(source, self.codecache)
        code = self.input_parser(codestr)
        idata = runner.run(code)
        self.history[codestr] = idata
        self.codecache.union(runner.code)
        return idata

    def get_history(self, index):
        for i, value in enumerate(self.history.values()):
            if i == index:
                return value
        return None

    def merge(self, fd):
        self.idata.merge(fd)

