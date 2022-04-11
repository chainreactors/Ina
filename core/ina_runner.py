import time

import click
import vthread
from queue import Queue

from settings import cidrcollect
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
            "fofa": FofaRunner(),
            "zoomeye": ZoomeyeRunner(),
            "hunter": HunterRunner()
        }
        if old_idata is not None:
            self.inadata = old_idata
        else:
            self.inadata = InaData(printdiff=True, printfunc=logging.info)

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
        # run_code 设计成生成器主要为了兼容run_pair
        if diffcode := self.code.get_diff_code_and_union(code):  # 去掉已查询过的待查询目标
            for engine in self.engines.values():
                if engine.name not in source:
                    continue
                engine.async_run_code(diffcode)

            for name in self.engines.keys():
                vthread.pool.wait("ina" + name)

            yield {engine.name: engine.get(diffcode) for engine in self.engines.values() if engine.get(diffcode)}
            return
        else:
            click.echo("all code already collected")

    def run_pair(self, code, source):
        if diffcode := self.code.get_diff_code_and_union(code):  # 去掉已查询过的待查询目标
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
        else:
            click.echo("all code already collected")

    def unique(self, data):
        pass

    def get_idata(self, code):
        return [engine.get_idata_from_cache(code) for engine in self.engines.values()]

    def concat_idata_from_cache(self, code):
        idata = InaData()
        for d in self.get_idata(code):
            idata.merge(d)
        return idata

    def concat_idata(self, data):
        # 从多个数据源中取数据, 并且合并成一个inadata
        idata = InaData()
        for name, d in data.items():
            idata.merge(self.engines[name].to_idata(d))
        return idata

    def queue_put(self, code, depth):
        self.codequeue.put((code, depth))

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

            if domains := diffs.top_domain:
                self.queue_put(Code(domain=domains, cert=domains), depth + 1)

            if icps := diffs.icp:
                self.queue_put(Code(icp=icps), depth + 1)

            # if icos := diffs.get("ico", None):
            #     self.queue_put(Code(ico=icos), depth)

    def run(self, code):
        self.queue_put(code, 1)

        while self.codequeue.qsize() > 0:  # 广度优先
            self.recu_run(*self.codequeue.get())
            time.sleep(1)

        # cidr 收集
        if cidrcollect:
            for data in self.run_code(Code(cidr=[c for c in self.inadata.cidr if c.split("/")[1] != "32"]), source="fofa"):
                diffs = self.inadata.merge(self.concat_idata(data))

        return self.inadata

    def run_once(self, code):
        datas = self.run_code(code, self.sources)
        return self.concat_idata(next(datas))
