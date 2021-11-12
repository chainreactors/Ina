from settings import *
import logging


class CheckDepth:
    cert = recu_cert
    domain = recu_domain
    icon_hash = recu_ico
    icp = recu_icp

    def __init__(self, func):
        self._func = func

    def too_deep(self,t,depth):
        if depth != 1 and depth >= CheckDepth.__dict__[t]:
            logging.warning("too depth")
            return True
        return False

    # def __call__(self, *args,fd,depth=1):
    #     if self.too_deep(args[0],depth):
    #         return
    #     return self._func(*args, fd=fd, depth=depth)

    def __get__(self, instance, owner):
        def wrap(*args, fd,depth=1):
            if self.too_deep(args[0], depth):
                return
            return self._func(instance, *args, fd=fd, depth=depth)
        return wrap
