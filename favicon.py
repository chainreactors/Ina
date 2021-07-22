import codecs
import mmh3
import requests
from hashlib import md5

from md5hash import md5hash
from mmh3hash import mmh3hash


def get_favicon(url):
    try:
        r = requests.get(url + "/favicon.ico")
        if r.status_code == 200:
            return codecs.lookup('base64').encode(r.content)[0]
        else:
            return False
    except:
        return False


def get_hash(url, hashtype="mmh3"):
    data = get_favicon(url)
    if not data:
        return None,None
    if hashtype == "mmh3":
        hash = mmh3.hash(data)
        name = mmh3hash.get(hash,None)
    elif hashtype == "md5":
        hash = md5(data).hexdigest()
        name = md5hash.get(hash,None)
    return hash, name
