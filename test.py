import vthread
from core import Ina
# import logging
if __name__ == '__main__':
    ina = Ina()
    vthread.unpatch_all()
    ina.run('domain="zjenergy.com.cn"').output(printer=print)
    # LOG_FORMAT = "%(asctime)s - %(message)s"
    # logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    # logging.getLogger().debug("aaa")
