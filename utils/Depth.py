from settings import *


class CheckDepth:
    cert = recu_cert
    domain = recu_domain
    icon_hash = recu_ico
    icp = recu_icp

    def __init__(self,func):
        self._func = func

    def __call__(self, *args,fd,depth=1):
        if depth != 1 and depth > CheckDepth.__dict__[args[0]]:
            print("too depth")
            return
        return self._func(*args,fd=fd,depth=depth)