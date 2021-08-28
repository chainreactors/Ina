from settings import *


class CheckDepth:
    cert = recu_cert
    domain = recu_domain
    ico = recu_ico
    icp = recu_icp

    def __init__(self,func):
        self._func = func

    def __call__(self, *args):
        if len(args) == 3 and args[2] > Depth.__dict__[args[0]]:
            print("too depth")
            return
        return self._func(*args)