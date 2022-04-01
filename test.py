from core import logging
from core import Ina
# import logging
if __name__ == '__main__':
    ina = Ina()
    ina.run('domain="zjenergy.com.cn"')
    # LOG_FORMAT = "%(asctime)s - %(message)s"
    # logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    # logging.getLogger().debug("aaa")
