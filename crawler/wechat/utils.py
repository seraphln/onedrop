# coding=utf8
#

import random


"""

"""


def save_to_file():
    pass


def generate_proxy(proxies):
    host, port, http_method = random.choice(proxies)
    proxy_dict = {http_method.lower(): 'http://%s:%s' % (host, port)}

    return proxy_dict, [host, port, http_method]

