import vthread
from queue import Queue

from . import logging
from .ina_code import Code
from .ina_data import InaData
from .depth import CheckDepth
from .fofa import FofaRunner
from .zoomeye import ZoomeyeRunner
from .hunter import HunterRunner


class InaRunner:
    def __init__(self, source="all", old_code=None, old_idata=None, keep_source=False):
        self.engines = {
            # "fofa": FofaRunner(),
            "zoomeye": ZoomeyeRunner(),
            # "hunter": HunterRunner()
        }
        if old_idata is not None:
            self.inadata = old_idata
        else:
            self.inadata = InaData(True, logging.info)

        if old_code is not None:
            self.code = old_code
        else:
            self.code = Code()

        if source == "all":
            self.sources = self.engines.keys()
        else:
            self.sources = source.split(",")

        self.cache = {}
        self.codequeue = Queue()
        self.keep_source = keep_source  # 用来收集数据来源, 大部分情况下并不需要知道数据来源,可以将多条语句合并查询减少api请求次数

    def run_code(self, code, source):
        if (diffcode := self.code.get_diff_code_and_union(code)) is not None:  # 去掉已查询过的待查询目标
            for engine in self.engines.values():
                if engine.name not in source:
                    continue
                engine.async_run_code(diffcode)

            for name in self.engines.keys():
                vthread.pool.wait("ina" + name)

            yield {engine.name: engine.get(diffcode) for engine in self.engines.values() if engine.get(diffcode)}
            return

    def run_pair(self, code, source):
        if (diffcode := self.code.get_diff_code_and_union(code)) is not None:  # 去掉已查询过的待查询目标
            for c in diffcode.params:
                for engine in self.engines.values():
                    if engine.name not in source:
                        continue
                    engine.async_run_code(c)
            # 每个engine都是单线程的, 等待全部engine完成任务
            for name in self.engines.keys():
                vthread.pool.wait("ina" + name)

            for c in diffcode.params:
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

    # def request_for_icp(self, urls):
    #     pass
    #
    # def request_for_icon(self, urls):
    #     pass

    def queue_put(self, code, depth):

        self.codequeue.put((code, depth+1))

    @CheckDepth
    def recu_run(self, code, depth=1):
        if self.keep_source:
            datas = self.run_pair(code, self.sources)
        else:
            datas = self.run_code(code, self.sources)

        for data in datas:
            if not data:  # 如果无数据,则跳过
                continue

            new_idata = self.concat_idata(data)
            diffs = self.inadata.merge(new_idata)

            # if urls := diffs.get("url", None):  # 通过云函数将所有url访问一遍, 并获取icp, iconhash等信息
            #     icps = self.request_for_icp(urls)
            #     if self.inadata.union("icp", icps):
            #         self.queue_put(Code(icp=icps), depth)
            #     icons = self.request_for_icon(urls)
            #     if self.inadata.union("ico", icons):
            #         self.queue_put(Code(icon=icons), depth)

            if domains := diffs.get("domain", None):
                self.queue_put(Code(domain=domains, cert=domains), depth)

            if icps := diffs.get("icp", None):
                self.queue_put(Code(icp=icps), depth)

            if icos := diffs.get("ico", None):
                self.queue_put(Code(ico=icos), depth)

    def run(self, code):
        self.queue_put(code, 0)

        while self.codequeue.qsize() > 0:  # 广度优先
            self.recu_run(*self.codequeue.get())

        # cidr 收集
        self.inadata.update_cidr()
        for data in self.run_code(Code(cidr=self.inadata["cidr"]), source="fofa"):
            new_idata = self.concat_idata(data)
            diffs = self.inadata.merge(new_idata)

        return self.inadata

