

from core import ZoomeyeClient, Code


if __name__ == '__main__':
    code = Code("zoomeye", cidr="47.95.116.67/28")
    zoo = ZoomeyeClient()
    zoo.query(str(code))