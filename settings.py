fofa_email = ""
fofa_key = ""
zoomeye_key = ""
hunter_key = ""


# 递归配置
recu = {
    "cert": 3,
    "domain": 3,
    "icp": 2,
    "ico": 2,
    "cidr": 1
}
cidrcollect = False

# request
mitm_proxy = {
    "http": "http://127.0.0.1:1080",
    "https": "http://127.0.0.1:1080"
}
requests_debug = {
    "proxies": {'https': 'http://127.0.0.1:8080',
           "http": 'http://127.0.0.1:8080'},
}

# debug
is_debug = False

