#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
from ipify import get_ip
from ipify.exceptions import ConnectionError, ServiceError

try:
    ip = get_ip()
    print("IP Address = ", ip)
except ConnectionError:
    print("network error")
    # If you get here, it means you were unable to reach the ipify service,
    # most likely because of a network error on your end.
except ServiceError:
    print("ipify error")
    # If you get here, it means ipify is having issues, so the request
    # couldn't be completed :(
except Exception as ex:
    print(str(ex))
    # Something else happened (non-ipify related). Maybe you hit CTRL-C
    # while the program was running, the kernel is killing your process, or
    # something else all together.
"""

import urllib.request

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

print(external_ip)
