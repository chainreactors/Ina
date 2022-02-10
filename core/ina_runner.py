import vthread
from queue import Queue

from .code import Code
from .fofa import FofaRunner
from .ina_data import InaData
from .depth import CheckDepth


class InaRunner:
    def __init__(self, keep_source=False):
        self.engines = {
            "fofa": FofaRunner(),
            # "zoomeye":
        }
        self.inadata = InaData(True)
        self.codequeue = Queue()
        self.code = Code()
        self.cache = {}
        self.keep_source = keep_source  # 用来收集数据来源, 大部分情况下并不需要知道数据来源,可以将多条语句合并查询减少api请求次数

    def run_code(self, code):
        if diffcodes := self.code.get_diff_code_and_union(code):  # 去掉已查询过的待查询目标
            for engine in self.engines.values():
                engine.async_run_code(diffcodes)

            for name in self.engines.keys():
                vthread.pool.wait("ina" + name)

            yield {engine.name: engine.get(diffcodes) for engine in self.engines.values() if engine.get(diffcodes)}

    def run_pair(self, code):
        if diffcodes := self.code.get_diff_code_and_union(code):  # 去掉已查询过的待查询目标
            for c in diffcodes.params:
                for engine in self.engines.values():
                    engine.async_run_code(c)
            # 每个engine都是单线程的, 等待全部engine完成任务
            for name in self.engines.keys():
                vthread.pool.wait("ina" + name)

            for c in diffcodes.params:
                yield {engine.name: engine.get(c) for engine in self.engines.values() if engine.get(c)}
            return

    def unique(self, data):
        pass

    def get_idata(self, code):
        return [engine.to_idata_from_cache(code) for engine in self.engines.values()]

    def concat_idata_from_cache(self, code):
        idata = InaData()
        for d in self.get_idata(code):
            idata.merge(d)
        return idata

    def concat_idata(self, data):
        idata = InaData()
        for name, d in data.items():
            idata.merge(self.engines[name].to_idata(d))
        return idata

    def request_for_icp(self, urls):
        pass

    def request_for_icon(self, urls):
        pass

    def queue_put(self, code, depth):
        self.codequeue.put((code, depth+1))

    @CheckDepth
    def recu_run(self, code, depth=1):
        if self.keep_source:
            datas = self.run_pair(code)
        else:
            datas = self.run_code(code)

        for data in datas:
            if not data:  # 如果fofa无数据,则退出
                return

            new_idata = self.concat_idata(data)
            diffs = self.inadata.merge(new_idata)

            if urls := diffs.get("url", None):
                icps = self.request_for_icp(urls)
                if self.inadata.union("icp", icps):
                    self.queue_put(Code(icp=icps), depth)
                icons = self.request_for_icon(urls)
                if self.inadata.union("ico", icons):
                    self.queue_put(Code(icon=icons), depth)

            if domains := diffs.get("domain", None):
                self.queue_put(Code(domain=domains, cert=domains), depth)

            if icps := diffs.get("icp", None):
                self.queue_put(Code(icp=icps), depth)

            if icos := diffs.get("ico", None):
                self.queue_put(Code(ico=icos), depth)
        # self.inadata

    def run(self, code):
        self.recu_run(code)
        while self.codequeue.qsize() > 0:
            self.recu_run(*self.codequeue.get())