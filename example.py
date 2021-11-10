from gevent import monkey
monkey.patch_all()

from core import *


if __name__ == '__main__':
    fofa = Fofa()
    fd = fofa.run('ip="47.95.116.67"')
    fd.outputdata()