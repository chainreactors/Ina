from settings import recu
from . import logging


class CheckDepth:

    def __init__(self, func):
        self._func = func

    def too_deep(self, t, depth):
        if depth != 1 and depth > recu[t]:
            logging.warning("%s too deep, auto return" % t)
            return True
        return False

    def __get__(self, instance, owner):
        def wrap(code, depth=1):
            if self.too_deep(code.major_type(), depth):
                return
            return self._func(instance, code, depth=depth)
        return wrap
