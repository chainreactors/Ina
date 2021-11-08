import logging
# Fofa_email_stolen = "hancool@163.com"
# Fofa_key_stolen = "238ebb08523bff5cf297b96364f62440"

# Fofa_email_company = "1477917783@qq.com"
# Fofa_key_company = "96cebd4dec3a195a7023a062e3e68c8f"

# fofa_email = "m09ic@foxmail.com"
# fofa_key = "6c67303712db0965d3a27a0e16132434"

# fofa_email = "admin@iswin.org"
# fofa_key = "dee4b9144c176bcf134faae4d6dc2ed5"


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


tyc_cookie = "auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzIyMTAyNDg0NCIsImlhdCI6MTYzNjM3NzY2MywiZXhwIjoxNjY3OTEzNjYzfQ.9Zq5s0RwaQ0W-mJ5iMv5m-BhQdekudwp4QD27McDbrrVgA9BkovJXZX7MMeru9rNVigxf9sUK4e1brT-M1LvCQ; acw_sc__v2=6107b2cbf9196c1e758e206607e2f878c9580c3c"