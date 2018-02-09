#!/usr/bin/python
""" example script to access the portal """

from __future__ import print_function
import sys
from pprint import pprint
from o2_scrap import O2mobile

reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == "__main__":

    USER = 'xxxxx'
    PASSWORD = '********'
    DEBUG = False

    # login to o2
    O2M = O2mobile()

    # login and get the browser object
    O2B = O2M.login(USER, PASSWORD, DEBUG)
    print(O2B)

    # get numbers under contract
    NUMBERS = O2M.get_numbers(O2B)
    pprint(NUMBERS)

    # get data-usage and contract information for a specific number
    DICTIONARY = O2M.get_overview(O2B, '0176-86939403')
    pprint(DICTIONARY)

    # get bills
    BILLS = O2M.get_bills(O2B)
    pprint(BILLS)
    
    if(not DEBUG):
        O2M.close_instance(O2B)