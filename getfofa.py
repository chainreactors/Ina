from gevent import monkey
monkey.patch_all()

from getfofa import *
from webtookit import *
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


def getcode(code):
    codes = code.split(" ")
    if os.path.exists(codes[-1]):
        s = loadfile(codes[-1])
    else:
        s = loadjson(" ".join(codes[1:]))
    if s and "getcompany" in s:
        return s["getcompany"]
    else:
        return ""


@click.command()
@click.option("--code", "-c", help="单条语句搜索,不递归爬取,无法与其他语句合并")
@click.option("--filename", "-f", help="输出文件名")
@click.option("--output", "-o", default="ip,domain,cidr")
def command(code, filename, output):
    main(code, filename, output)


def main(code, filename, output):
    fofa = Fofa()

    if filename:
        outfunc = partial(write2file, filename=filename)
    else:
        outfunc = print

    if code:
        data = fofa.get_fofa(code)
        fofa.combine_fofa_result(fofa.fd, data)
        print()
        fofa.fd.outputdata(["ico", "ip", "icp", "url", "domain", "cidr"], outfunc=outfunc)
        exit(0)

    fds = {}
    index = 0
    while (fofacode := click.prompt("input fofa query")) != "exit":
        if fofacode.startswith("from"):
            j = getcode(fofacode)
            if j:
                fofacode = join_fofaqueries(domain=j)
            else:
                continue
        index += 1
        tmpfd = fofa.run(fofacode)
        fds[index] = (fofacode, tmpfd)
        if sum([len(i) for i in fofa.fd.diffs_fd(tmpfd)]):
            logging.info("found new assets:")
            (tmpfd - fofa.fd).outputdata(output.split(","), outfunc=outfunc)
        else:
            logging.info("not found new asset")

        while out := click.prompt(
                "choice output(ip,cidr,ico,icp,url,domain) or enter [help], [c|continue], [exit], [diff], [merge], [to_file <filename>]"):
            if out == "exit":
                exit()
            elif out == "":
                continue
            elif out in ["continue", "c"]:  # 如果输入continue,则爬下一条fofa语句
                break
            elif out == "diff":
                logging.info("print new assets different from fd")
                (tmpfd - fofa.fd).outputdata(outfunc=outfunc)
            elif "merge" in out:
                if len(v := out.split(" ")) == 1:
                    fofa.fd.merge(tmpfd)
                else:
                    fofa.fd.merge(fds[v][1])
                logging.info("merge success")
            elif "to_file" in out:
                outs = out.split(" ")
                if len(outs) >= 2 or filename:
                    tmpfilename = filename if filename else outs[-1]
                    printfunc = partial(write2file, filename=tmpfilename)
                    fofa.fd.outputdata(outfunc=printfunc)
                else:
                    print("please input filename,example: to_file out.txt")
                    continue
            elif out == "help":
                pass
            elif out == "history":
                [print(i, v[0]) for i, v in fds.items()]
            else:
                fofa.fd.outputdata(out.split(","), outfunc=print)


if __name__ == '__main__':
    command()
