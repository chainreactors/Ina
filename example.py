from core import *

if __name__ == '__main__':
    runner = InaRunner("hunter")
    code = Code(code='domain="zjenergy.com.cn"')
    idata = runner.run(code)
    print(idata.to_dict())