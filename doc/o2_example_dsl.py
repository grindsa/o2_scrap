#!/usr/bin/python
""" joerns o2 check tool """

from __future__ import print_function
import sys
import time
from o2_scrap import O2dsl
from pprint import pprint

if sys.version_info > (3, 0):
    import importlib
    importlib.reload(sys)
else:
    reload(sys)
    sys.setdefaultencoding('utf8')

if __name__ == "__main__":

    USER = 'xxxxxxxxxxx'
    PASSWORD = '*********'
    DEBUG = False

    with O2dsl(USER, PASSWORD, DEBUG) as O2D:
        USAGE_DICT = O2D.get_overview()
        pprint(USAGE_DICT)



