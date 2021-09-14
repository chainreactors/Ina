from collections import Counter


def count(data):
    return Counter(data)


def getvalues(gevenlets):
    return [i.value for i in gevenlets]


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def filter_ico(jobs):
    if jobs == None:
        return []
    icohashs = [str(i[0]) for i in getvalues(jobs) if i[0] and not i[1]]
    return [k for k, v in Counter(icohashs).items() if v >= 3]


def write2file(string,filename):
    tmp = open(filename, "a+",encoding="utf-8")
    tmp.write(string)
    tmp.close()

