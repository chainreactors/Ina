# from gevent import monkey
# monkey.patch_all()

from core import *
import click,json,os,logging
from functools import partial


def loadfile(filename):
    f = open(filename, "r", encoding="utf-8")
    s = f.read()
    return loadjson(s)


def loadjson(s):
    try:
        return json.loads(s)
    except:
        return ""


@click.command()
@click.option("--code", "-c", help="单条语句搜索,不递归爬取,无法与其他语句合并")
@click.option("--filename", "-f", help="输出文件名")
@click.option("--output", "-o", default="ip,domain,cidr")
def command(code, filename, output):
    main(code, filename, output)


def main(code, filename, output):
    ina = Ina()
    ina.run('domain="zjenergy.com.cn"')
#
# def main(code, filename, output):
#     fofa = Fofa()
#
#     # 初始化输出位置
#     if filename:
#         outfunc = partial(write2file, filename=filename)
#     else:
#         outfunc = print
#
#     # 单条fofa语句
#     if code:
#         fd = fofa.run_code(code)
#         fd.output(["ico", "ip", "icp", "url", "domain", "cidr"], outfunc=outfunc)
#         exit(0)
#
#     # 交互式
#     while (fofacode := click.prompt("input fofa query")) != "exit":
#         tmpfd = fofa.run_code(fofacode)
#         if sum([len(i) for i in fofa.fd.diffs_fd(tmpfd)]):
#             logging.info("found new assets:")
#             (tmpfd - fofa.fd).output(output.split(","), outfunc=outfunc)
#         else:
#             logging.info("not found new asset")
#
#         while out := click.prompt(
#                 "choice output(ip,cidr,ico,icp,url,domain) or enter [help], [c|continue], [exit], [diff], [merge], [to_file <filename>]"):
#             if out == "exit":
#                 exit()
#             elif out == "":
#                 continue
#             elif out in ["continue", "c"]:  # 如果输入continue,则爬下一条fofa语句
#                 break
#             elif out == "diff":
#                 logging.info("print new assets different from fd")
#                 (tmpfd - fofa.fd).output(outfunc=outfunc)
#             elif "merge" in out:
#                 if len(v := out.split(" ")) == 1:
#                     fofa.fd.merge(tmpfd)
#                 else:
#                     fofa.fd.merge(fds[v][1])
#                 logging.info("merge success")
#             elif "to_file" in out:
#                 outs = out.split(" ")
#                 if len(outs) >= 2 or filename:
#                     tmpfilename = filename if filename else outs[-1]
#                     printfunc = partial(write2file, filename=tmpfilename)
#                     fofa.fd.output(outfunc=printfunc)
#                 else:
#                     print("please input filename,example: to_file out.txt")
#                     continue
#             elif out == "help":
#                 pass
#             elif out == "history":
#                 [print(i, v[0]) for i, v in fds.items()]
#             else:
#                 fofa.fd.output(out.split(","), outfunc=print)


if __name__ == '__main__':
    command()
