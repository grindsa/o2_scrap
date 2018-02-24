#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" dkb internet banking automation library """

from __future__ import print_function
import sys
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

if sys.version_info > (3, 0):
    import importlib
    importlib.reload(sys)
else:
    reload(sys)
    sys.setdefaultencoding('utf8')

def wait_for_element(driver, ele, etype, timeout):
    """ this function monitors a html page before executing the script further
        and waits for an element to appear

        args:
            driver  - selenium driver object
            ele     - element to wait for
            etype   - element time (could be ID or NAME)
            timeout - time to wait in seconds

        returns:
            True - in case the element was found
            False - if timeout kicks in and aborts the function
    """
    try:
        if etype == 'id':
            element_present = EC.element_to_be_clickable((By.ID, ele))
        elif etype == 'id-starts-with':
            element_present = EC.element_to_be_clickable((By.XPATH, '//*[starts-with(@id,"%s")]' % ele))
        elif etype == 'name':
            element_present = EC.element_to_be_clickable((By.NAME, ele))
        elif etype == 'class':
            element_present = EC.element_to_be_clickable((By.CLASS_NAME, ele))
        else:
            element_present = EC.presence_of_element_located((By.XPATH, '//%s[text()="%s"]' % (etype, ele)))

        WebDriverWait(driver, timeout).until(element_present)
        return True
    except TimeoutException:
        print("Timed out waiting for page to load")
        return False

def wait_for_element_to_disappear(driver, ele, etype, timeout):
    """ this function monitors a html page before executing the script further
        and waits for an element to disappear

        args:
            driver  - selenium driver object
            ele     - element to wait for
            etype   - element time (could be ID or NAME)
            timeout - time to wait in seconds

        returns:
            True - in case the element was found
            False - if timeout kicks in and aborts the function
    """
    try:
        if etype == 'id':
            element_not_present = EC.invisibility_of_element_located((By.ID, ele))
        elif etype == 'name':
            element_not_present = EC.invisibility_of_element_located((By.NAME, ele))
        elif etype == 'class':
            element_not_present = EC.invisibility_of_element_located((By.CLASS_NAME, ele))
        else:
            element_not_present = EC.invisibility_of_element_located((By.NAME, ele))

        WebDriverWait(driver, timeout).until(element_not_present)
        return True
    except TimeoutException:
        print("Timed out waiting for element to disappear")
        return False

class O2mobile(object):
    """ class to fetch information from mobile accounts """

    base_url = 'https://www.o2online.de'
    user = None
    pwd = None
    driver = None
    debug = False

    def __init__(self, user=None, pwd=None, debug=False):
        self.user = user
        self.pwd = pwd
        self.debug = debug

    def __enter__(self):
        """
        Makes DKBRobo a Context Manager

        with DKBRobo("user","pwd") as dkb:
            print (dkb.lastlogin)
        """
        if not self.driver:
            self.login()
        return self

    def __exit__(self, *args):
        """
        Close the connection at the end of the context
        """
        self.logout()

    def auth(self):
        """ authenticates towards an o2 portal by using a user password combination

            args:
                self - self

            returns:
                None
        """
        if wait_for_element(self.driver, 'IDToken1', 'id', 15):
            try:
                username = self.driver.find_element_by_id("IDToken1")
                password = self.driver.find_element_by_id("IDToken2")
                username.send_keys(self.user)
                password.send_keys(self.pwd)
                btns = self.driver.find_element_by_xpath("//*[contains(text(), 'Einloggen')]")
                btns.click()
            except NoSuchElementException:
                pass

    def close_instance(self):
        """ closes an existing selenium web driver instance by using either PhantomJS or Mozilla

            args:
                self - self

            returns:
                None
        """
        self.driver.close()
        return None

    def get_bills(self):
        """ get list of bills per month

            args:
                self - self

            returns:
                bill_list - list of bills
        """
        link = self.driver.find_element_by_link_text('Rechnung')
        link.click()
        if wait_for_element(self.driver, 'panel-action', 'class', 35):
            soup = BeautifulSoup(self.driver.find_element_by_class_name('panel-group-stripped').get_attribute('innerHTML'), 'html5lib')
            bill_list = []
            for bill in soup.findAll('div', attrs={'class':'panel panel-action'},):
                tmp_dict = {}
                tmp_dict['price'] = bill.find('div', attrs={'class': 'price-single price-single-lg'}).text.strip()
                tmp_dict['text'] = bill.find('div', attrs={'class': 'text'}).text.strip()
                tmp_dict['download'] = self.base_url + '/ecare' + bill.find('a')['href'].lstrip('.')

                bill_list.append(tmp_dict)

        return bill_list

    def get_numbers(self):
        """ get phone numbers belonging to the contract-choice-link

            args:
                self - self

            returns:
                number_dict - dictionary of phone numbers and plan names
        """
        ele = self.driver.find_element_by_class_name('side-nav-contract-choice-link')
        ele.click()

        soup = BeautifulSoup(self.driver.find_element_by_class_name('side-nav-contract-choice-menu-items').get_attribute('innerHTML'), 'html5lib')

        ele = self.driver.find_element_by_class_name('side-nav-contract-choice-link')
        ele.click()

        number_dict = {}
        for llist in soup.findAll('li'):
            spans = llist.findAll('span')
            try:
                number_dict[spans[1].text.strip()] = spans[0].text.strip()
            except IndexError:
                pass

        return number_dict

    def get_overview(self, number):
        """ get data consumption and contract details for a given number

        args:
            number - number to check

        returns:
            number_dict - dictionary details
        """

        wait_for_element(self.driver, 'navigation-label', 'class', 25)
        html = self.driver.page_source

        try:
            # ele = self.driver.find_element_by_xpath("//span[contains(text(), 'Mein O')]")
            ele = self.driver.find_element_by_xpath("//span[contains(text(), 'Übersicht')]")
            ele.click()
            wait_for_element(self.driver, 'tariff-attributes', 'class', 25)
        except NoSuchElementException:
            pass

        try:
            soup = BeautifulSoup(self.driver.find_element_by_class_name('side-nav-contract-choice-link').get_attribute('innerHTML'), 'html5lib')
            spans = soup.findAll('span')
            dnumber = spans[1].text.strip()
        except IndexError:
            dnumber = None

        result = False
        if number != dnumber:
            result = self.switch_number(number)
        else:
            result = True

        number_dict = {}
        if result:
            panels = self.driver.find_elements_by_class_name('csc-panel')
            # get data usage
            number_dict['data-usage'] = {}
            soup = BeautifulSoup(panels[0].get_attribute('innerHTML'), 'html5lib')
            try:
                block = soup.find('div', attrs={'class':'usage-info'},)
                spans = block.findAll('span')
                number_dict['data-usage']['current'] = '{0} {1}'.format(spans[0].text.strip(), spans[1].text.strip())
                number_dict['data-usage']['limit'] = spans[2].text.strip()
                number_dict['data-usage']['autoadjust'] = soup.find('div', attrs={'class':'usage-items-small'},).text.strip()
                number_dict['data-usage']['remaining'] = soup.find('span', attrs={'class':'highlight small'},).text.strip()
            except IndexError:
                pass
            except AttributeError:
                pass

            # get plan data
            number_dict['plan-data'] = {}
            if wait_for_element(self.driver, 'tariff-attributes', 'class', 25):
                soup = BeautifulSoup(panels[1].get_attribute('innerHTML'), 'html5lib')

                number_dict['plan-data']['tariff'] = soup.find('h2', attrs={'class':'h2 highlight'},).text.strip()
                try:
                    number_dict['plan-data']['price'] = soup.find('div', attrs={'class':'price-single'},).text.strip()
                except AttributeError:
                    pass

                dlitem = soup.find("dl")
                keys = dlitem.findAll('dt')
                values = dlitem.findAll('dd')

                cnt = 0
                for key in keys:
                    number_dict['plan-data'][key.text.strip()] = values[cnt].text.strip()
                    cnt += 1

        return number_dict

    def login(self):
        """ used to login towards an o2-online portal calling the following methods:
                1. new - to start a new instance
                2. get - to openan http connection
                3. auth - to authenticates by using username and password

            args:
                user      - username
                password  - password
                debug     - show browser window (require gecko-engine)

            returns:
                Upon successfull login a reference to a selenium driver object will be returned.
                Otherwise the resturn code will be "False" and an error message get printed on STDOUT
        """
        self.driver = self.new_instance()
        # open page
        try:
            self.driver.get('https://login.o2online.de/auth/login')
        except TimeoutException:
            print('timeout connecting to {0}'.format('https://login.o2online.de/auth/login'))
            sys.exit(0)

        self.auth()

        # catch login error
        try:
            error = self.driver.find_element_by_xpath('//div[contains(@class, "alert") and contains(@class, "alert-danger")]').text.strip()
        except NoSuchElementException:
            error = None

        if error:
            print('Login failed: {0}'.format(error))
            self.close_instance()
            sys.exit(0)
            return None
        else:
            link = self.driver.find_element_by_link_text('Mein Verbrauch')
            link.click()

            if wait_for_element(self.driver, 'tariff-attributes', 'class', 25):

                # get rid of this f**** advertisement popups
                if wait_for_element(self.driver, 'btn', 'class', 5):
                    btn = self.driver.find_element_by_xpath('//button[contains(@class, "btn")]')
                    btn.click()
                return True
            else:
                self.close_instance()
                sys.exit(0)
                return None

    def logout(self):
        """ logout method """
        ele = self.driver.find_element_by_class_name('glyphicon-user')
        ele.click()
        ele = self.driver.find_element_by_xpath("//span[contains(text(), 'Logout')]")
        ele.click()
        self.close_instance()

    def new_instance(self):
        """ initializes a new selenium web driver instance by using either PhantomJS or Mozilla
            and returns a reference to the browser object for further processing

            args:
                debug - debug mode

            returns:
                None
        """
        driver = webdriver.PhantomJS()
        if self.debug:
            driver = webdriver.Firefox()
        driver.set_window_size(1024, 768)
        driver.set_script_timeout(5)
        return driver

    def switch_number(self, number):
        """ switch to a different phone number in o2 web portal

            args:
                number - phone number

            returns:
                True - in case the switch was successful
                False - in case switch failed

        """
        ele = self.driver.find_element_by_class_name('side-nav-contract-choice-link')
        ele.click()

        if wait_for_element(self.driver, 'side-nav-contract-choice-menu-items', 'class', 25):
            try:
                ele = self.driver.find_element_by_xpath("//span[contains(text(), '%s')]" % number)
                ele.click()
                if wait_for_element_to_disappear(self.driver, 'tariff-attributes', 'class', 35):
                    return wait_for_element(self.driver, 'tariff-attributes', 'class', 25)
                else:
                    return False
            except NoSuchElementException:
                print('number "{0}" could no tbe found in portal'.format(number))
                return False
        else:
            return False

class O2dsl(object):
    """ class to fetch information from dsl accounts """

    base_url = 'https://dsl.o2online.de/'
    user = None
    pwd = None
    driver = None
    debug = False

    def __init__(self, user=None, pwd=None, debug=False):
        self.user = user
        self.pwd = pwd
        self.debug = debug

    def __enter__(self):
        """
        Makes DKBRobo a Context Manager

        with DKBRobo("user","pwd") as dkb:
            print (dkb.lastlogin)
        """
        if not self.driver:
            self.login()
        return self

    def __exit__(self, *args):
        """
        Close the connection at the end of the context
        """
        self.logout()

    def auth(self):
        """ authenticates towards an o2 portal by using a user password combination

            args:
                self - self

            returns:
                None
        """
        if wait_for_element(self.driver, 'benutzername', 'id', 15):
            try:
                username = self.driver.find_element_by_id("benutzername")
                password = self.driver.find_element_by_id("passwort")
                username.send_keys(self.user)
                password.send_keys(self.pwd)
                btns = self.driver.find_element_by_id('loginButton')
                btns.click()
            except NoSuchElementException:
                pass

    def close_instance(self):
        """ closes an existing selenium web driver instance by using either PhantomJS or Mozilla

            args:
                self - self

            returns:
                None
        """
        if not self.debug:
            self.driver.close()
        return None

    def get_overview(self):
        """ get data consumption

        args:
            self - self

        returns:
            usage_dict - dictionary with details
        """
        self.driver.get(self.base_url + 'selfcare/content/segment/kundencenter/meindslfestnetz/dslverbrauch/')

        if wait_for_element(self.driver, 'usageoverview', 'class', 15):
            soup = BeautifulSoup(self.driver.page_source, 'html5lib')
            data_dic = {}

            # collect actual usage
            ublock = soup.find('div', attrs={'class':'datablock usedvolume'},)
            (used_volume, limit) = ublock.find('div', attrs={'class':'value'},).text.strip().split('/')
            limit = limit.replace(' GB', '')

            data_dic['used'] = int(used_volume.rstrip(' '))
            data_dic['limit'] = int(limit.lstrip(' '))
            data_dic['since'] = ublock.find('div', attrs={'class':'label'},).text.strip()
            data_dic['remaining'] = ublock.find('div', attrs={'class':'textblock'},).text.strip()

            # collect prognosed usage
            ublock = soup.find('div', attrs={'class':'datablock prognosedvolume'},)
            (prognosed_volume, _dummy) = ublock.find('div', attrs={'class':'value'},).text.strip().split('/')
            data_dic['prognosed'] = int(prognosed_volume.rstrip(' '))

            # create 6 months usage history
            data_dic['history'] = []
            ublock = soup.find('div', attrs={'id':'throttleoverview'},)
            for mlist in ublock.findAll('li'):
                # build temporary hash to be added to list
                tmp_dic = {}
                tmp_dic['usage'] = int(mlist.find('span').text.strip().replace(' GB', ''))

                (from_date, to_date) = mlist.find('div', attrs={'class':'month'},).text.strip().split(' ')
                tmp_dic['from'] = from_date
                tmp_dic['to'] = to_date

                data_dic['history'].append(tmp_dic)

        return data_dic

    def login(self):
        """ used to login towards an o2-online portal calling the following methods:

            args:
                self - self

            returns:
                Upon successfull login a reference to a selenium driver object will be returned.
                Otherwise the resturn code will be "False" and an error message get printed on STDOUT
        """
        self.driver = self.new_instance()
        # open page
        try:
            self.driver.get(self.base_url + 'sso/login')
        except TimeoutException:
            print('error connecting to {0}'.format(self.base_url + 'sso/login'))
            sys.exit(0)

        self.auth()

        # catch login error
        try:
            self.driver.find_element_by_class_name('alert')
            print('Login failed! Aborting...')
            sys.exit(0)
            return False
        except NoSuchElementException:
            return wait_for_element(self.driver, 'usedvolume', 'class', 15)

    def logout(self):
        """ logout mothod

            args:
                self - self
            returns:
                none
        """
        btn = self.driver.find_element_by_class_name('logoutUser')
        btn.click()
        self.close_instance()


    def new_instance(self):
        """ initializes a new selenium web driver instance by using either PhantomJS or Mozilla
            and returns a reference to the browser object for further processing

            args:
                self - self

            returns:
                None
        """
        driver = webdriver.PhantomJS()
        if self.debug:
            driver = webdriver.Firefox()
        driver.set_window_size(1024, 768)
        driver.set_script_timeout(5)
        return driver
