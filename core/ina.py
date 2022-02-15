from .ina_data import InaData
from .ina_runner import InaRunner
from .code import Code
from . import logging


class Ina:
    def __init__(self):
        self.idata = InaData(True, logging.info)
        self.history = {}

    def input_parser(self, input):
        code = Code(code=input)
        return code

    def run(self, code):
        fr = InaRunner()
        code = self.input_parser(code)
        idata = fr.run(code)
        self.history[str(code)] = idata
        return idata

    def get_history(self, index):
        for i, value in enumerate(self.history.values()):
            if i == index:
                return value
        return None
        # if len(self.history_data) > index:
        #     return self.history_data[index]

    # def idata_update(self, fd):
    #     pass

    def merge(self, fd):
        self.idata.merge(fd)

