import logging


INFO_FORMAT = "%(levelname)s %(message)s"
ERROR_FORMAT = "%(levelname)s %(message)s"
logging.basicConfig(level=logging.INFO, format=INFO_FORMAT)
logging.basicConfig(level=logging.ERROR, format=ERROR_FORMAT)

# 递归配置
recu_cert = 3
recu_domain = 3
recu_icp = 3
recu_ico = 2
recu_cidr = 1
cidrcollect = False


tyc_cookie = "auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzIyMTAyNDg0NCIsImlhdCI6MTYzNjM3NzY2MywiZXhwIjoxNjY3OTEzNjYzfQ.9Zq5s0RwaQ0W-mJ5iMv5m-BhQdekudwp4QD27McDbrrVgA9BkovJXZX7MMeru9rNVigxf9sUK4e1brT-M1LvCQ; acw_sc__v2=6107b2cbf9196c1e758e206607e2f878c9580c3c"