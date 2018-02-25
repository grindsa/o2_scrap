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

    # login to o2
    with O2mobile(USER, PASSWORD, DEBUG) as O2M:
    
        NUMBERS = O2M.get_numbers()
        pprint(NUMBERS) 

        # get data-usage and contract information for a specific number
        DICTIONARY = O2M.get_overview('0176-XXXXXX')
        pprint(DICTIONARY)

        # get bills
        BILLS = O2M.get_bills()
        pprint(BILLS)
