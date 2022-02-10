from .ina_data import InaData
from .ina_runner import InaRunner
from .code import Code


class Ina:
    def __init__(self):
        self.idata = InaData()
        self.history_data = []

    def input_parser(self, input):
        code = Code(code=input)
        return code

    def run(self, code):
        fr = InaRunner()
        code = self.input_parser(code)
        fd = fr.run_code(code)
        # self.history_append(code, fd)
        return fd

    def append_history(self, fc, fd):
        self.history_data.append((str(fc), fd))

    def get_history(self, index):
        if len(self.history_data) > index:
            return self.history_data[index]

    def idata_update(self, fd):
        pass

    def merge(self, fd):
        self.idata.merge(fd)

