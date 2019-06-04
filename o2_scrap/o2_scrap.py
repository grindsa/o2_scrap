#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" o2online screen scrap library """

from __future__ import print_function
import sys
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options

if sys.version_info > (3, 0):
    import importlib
    importlib.reload(sys)
else:
    reload(sys)
    sys.setdefaultencoding('utf8')

def print_debug(debug, text):
    """ little helper to print debug messages """
    if debug:
        print('{0}: {1}'.format(datetime.now(), text))

def wait_for_element(driver, debug, ele, etype, timeout):
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
    print_debug(debug, 'wait_for_element: {0}:{1}:{2}'.format(etype, ele, timeout))
    try:
        if etype == 'id':
            element_present = EC.element_to_be_clickable((By.ID, ele))
        elif etype == 'id-starts-with':
            element_present = EC.element_to_be_clickable((By.XPATH, '//*[starts-with(@id,"%s")]' % ele))
        elif etype == 'name':
            element_present = EC.element_to_be_clickable((By.NAME, ele))
        elif etype == 'class':
            element_present = EC.element_to_be_clickable((By.CLASS_NAME, ele))
            # element_present = EC.presence_of_element_located((By.XPATH, '//@class, "%s"]' % (ele)))
        else:
            element_present = EC.presence_of_element_located((By.XPATH, '//%s[text()="%s"]' % (etype, ele)))

        WebDriverWait(driver, timeout).until(element_present)
        print_debug(debug, "found {0}:{1}".format(etype, ele))
        return True
    except TimeoutException:
        print_debug(debug, "Timed out waiting for page to load {0}:{1}".format(etype, ele))
        return False

def wait_for_element_to_disappear(driver, _debug, ele, etype, timeout):
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

    def __init__(self, user=None, pwd=None, debug=False, headless=True):
        self.user = user
        self.pwd = pwd
        self.debug = debug
        self.headless = headless

    def __enter__(self):
        """
        Makes DKBRobo a Context Manager

        with DKBRobo("user","pwd") as dkb:
            print (dkb.lastlogin)
        """
        if not self.driver:
            self.login()
            print_debug(self.debug, 'self.login() done')
        return self

    def __exit__(self, *args):
        """
        Close the connection at the end of the context
        """
        print_debug(self.debug, 'we are in __exit__')
        # self.logout()

    def auth(self):
        """ authenticates towards an o2 portal by using a user password combination

            args:
                self - self

            returns:
                None
        """
        print_debug(self.debug, 'auth started')
        if self.debug:
            self.driver.save_screenshot('01-auth-in.png')
        if wait_for_element(self.driver, self.debug, 'IDToken1', 'id', 15):
            try:
                username = self.driver.find_element_by_id("IDToken1")
                password = self.driver.find_element_by_id("IDToken2")
                username.send_keys(self.user)
                password.send_keys(self.pwd)
                btns = self.driver.find_element_by_xpath("//*[contains(text(), 'Einloggen')]")
                btns.click()
                if self.debug:
                    self.driver.save_screenshot('02-auth-after-login.png')
            except NoSuchElementException:
                if self.debug:
                    self.driver.save_screenshot('02-auth-exception.png')
        print_debug(self.debug, 'auth done')

    def catch_ads(self):
        """ catch ads """
        try:
            ads = self.driver.find_element_by_xpath('//button[@class="btn"]')
            ads.click()
            print_debug(self.debug, 'pressed button to close overlay window')
        except BaseException:
            print_debug(self.debug, 'no add found')

    def catch_cookies(self):
        """ catch cookies """
        print_debug(self.debug, "catch_cookies()")
        if wait_for_element(self.driver, self.debug, 'uc-btn-accept-banner', 'id', 5):
            print_debug(self.debug, 'found uc-btn-accept-banner')
            btn = self.driver.find_element_by_id("uc-btn-accept-banner")
            btn.click()
        else:
            if self.debug:
                self.driver.save_screenshot('06-cookie.png')
            print_debug(self.debug, 'cookie message wait done')

        print_debug(self.debug, 'catch_cookies() ended')

    def catch_optin(self):
        """ catch and accept optin """
        print_debug(self.debug, "catch_optin()")
        if wait_for_element(self.driver, self.debug, 'optinAcceptButton', 'id', 5):
            print_debug(self.debug, 'found optinAcceptButton')
            btn = self.driver.find_element_by_id("optinAcceptButton")
            btn.click()
        else:
            if self.debug:
                self.driver.save_screenshot('05-optin.png')
        print_debug(self.debug, 'catch_optin() ended')

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
        if wait_for_element(self.driver, self.debug, 'panel-action', 'class', 35):
            soup = BeautifulSoup(self.driver.find_element_by_class_name('panel-group-stripped').get_attribute('innerHTML'), 'html5lib')
            bill_list = []
            for bill in soup.findAll('div', attrs={'class':'panel panel-action'},):
                tmp_dict = {}
                tmp_dict['price'] = bill.find('div', attrs={'class': 'price-single price-single-lg'}).text.strip()
                tmp_dict['text'] = bill.find('div', attrs={'class': 'text'}).text.strip()
                tmp_dict['download'] = self.base_url + '/ecare' + bill.find('a')['href'].lstrip('.')

                bill_list.append(tmp_dict)

        return bill_list

    def get_data_usage(self):
        """ get usage data """
        data_dic = {}
        if wait_for_element(self.driver, self.debug, 'usage-status-summary', 'class', 25):
            print_debug(self.debug, 'usage-status-summary')
            if self.debug:
                self.driver.save_screenshot('10-user-status-summary-succ.png')

            soup = BeautifulSoup(self.driver.find_element_by_tag_name('usage-monitor-wrapper').get_attribute('innerHTML'), 'lxml')
            # actual data usage
            try:
                data_dic['current'] = soup.find('span', attrs={'class':'usage-status-summary-quantity'}).text.strip() + ' ' + soup.find('span', attrs={'class':'usage-status-summary-entity'}).text.strip()
            except BaseException:
                data_dic['current'] = 'unknown'
            # limit
            try:
                limit = 'unk'
                limits = soup.findAll('div', attrs={'class':'usage-status-summary-line'})
                for lim in limits:
                    if 'GB' in lim.text.strip():
                        limit = lim.find('strong').text.strip()
                        limit = re.sub(r'\s+', ' ', limit)
                        break
                data_dic['limit'] = limit
            except BaseException:
                data_dic['limit'] = 'unknown'
            # remaining
            try:
                data_dic['remaining'] = soup.find('h3').text.strip().replace('\n', ' ')
            except BaseException:
                data_dic['remaining'] = 'unknown'

        else:
            print_debug(self.debug, 'usage-status-summary NOT found')
            if self.debug:
                self.driver.save_screenshot('10-user-status-summary-failed.png')
        return data_dic

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
        print_debug(self.debug, 'get_overview({0})'.format(number))
        wait_for_element(self.driver, self.debug, 'navigation-label', 'class', 25)
        print_debug(self.debug, 'wait for navigation-label done')
        result = self.switch_number(number)
        time.sleep(2)
        number_dict = {}
        if result:

            # usage data
            number_dict['data-usage'] = self.get_data_usage()

            # plan data
            try:
                link = self.driver.find_element_by_link_text('Tarif und Vertrag')
                link.click()
                number_dict['plan-data'] = self.tarif_und_vertrag()
            except BaseException:
                try:
                    link = self.driver.find_element_by_link_text('Tarif & SIM-Karte')
                    link.click()
                    number_dict['plan-data'] = self.tarif_und_sim()
                except BaseException:
                    print_debug(self.debug, 'panel-tariff-contract NOT found')
                    if self.debug:
                        self.driver.save_screenshot('11-panel-tariff-contract-failed.png')
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
            # self.driver.get('https://login.o2online.de/auth/login?goto=https%3A%2F%2Fwww.o2online.de%2Fmein-o2%2F')
            self.driver.get('https://login.o2online.de/auth/login')
        except TimeoutException:
            print('timeout connecting to {0}'.format('https://login.o2online.de/auth/login'))
            sys.exit(0)

        if self.debug:
            self.driver.save_screenshot('00-login.png')

        print_debug(self.debug, 'login-site fetched')
        self.auth()

        # catch login error
        try:
            error = self.driver.find_element_by_xpath('//div[contains(@class, "alert") and contains(@class, "alert-danger")]').text.strip()
        except NoSuchElementException:
            error = None
        print_debug(self.debug, 'login error handling completed')

        if error:
            print('Login failed: {0}'.format(error))
            self.close_instance()
            sys.exit(0)
            return None
        else:

            # catch and confirm optin
            self.catch_optin()

            # catch cookie-message
            self.catch_cookies()

            try:
                link = self.driver.find_element_by_link_text('Verbrauch')
                link.click()
                print_debug(self.debug, 'Verbrauch click')
            except BaseException:
                print_debug(self.debug, 'Verbrauch failed')

            if self.debug:
                self.driver.save_screenshot('07-mv.png')

            if wait_for_element(self.driver, self.debug, 'usage-status-summary', 'class', 25):
                print_debug(self.debug, 'usage-status-summary')
                if self.debug:
                    self.driver.save_screenshot('08-user-status-summary-succ.png')

                # get rid of this f**** advertisement pop-ups
                self.catch_ads()

                if self.debug:
                    self.driver.save_screenshot('09-end-login.png')
                print_debug(self.debug, 'we will return true now')
                return True
            else:
                print_debug(self.debug, 'usage-status-summary NOT found')
                self.driver.save_screenshot('08-user-status-summary-failed.png')
                self.close_instance()
                sys.exit(0)
                return False

    def logout(self):
        """ logout method """
        print_debug(self.debug, 'looking for logout link')
        link = self.driver.find_element_by_link_text('Mein O2')
        link.click()
        #ele = self.driver.find_element_by_xpath('//a[@href="https://login.o2online.de/auth/logout"]')
        #ele.click()
        print_debug(self.debug, 'looking for logout button')
        link = self.driver.find_element_by_link_text('Logout')
        link.click()
        # ele = self.driver.find_element_by_xpath("//*[contains(text(), 'Logout')]")
        # ele.click()
        self.close_instance()

    def new_instance(self):
        """ initializes a new selenium web driver instance by using either PhantomJS or Mozilla
            and returns a reference to the browser object for further processing """
        options = Options()
        if self.headless:
            print_debug(self.debug, 'actiating headless mode')
            options.add_argument('-headless')
        driver = webdriver.Firefox(firefox_options=options)
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
        print_debug(self.debug, 'switch_number({0})'.format(number))
        ele = self.driver.find_element_by_class_name('side-nav-contract-choice-link')
        ele.click()
        print_debug(self.debug, 'side-nav-contract-choice-link clicked')
        if wait_for_element(self.driver, self.debug, 'side-nav-contract-choice-menu-items', 'class', 25):
            print_debug(self.debug, 'found side-nav-contract-choice-menu-items')
            try:
                ele = self.driver.find_element_by_xpath("//span[contains(text(), '%s')]" % number)
                ele.click()
                print_debug(self.debug, 'found list-entry for number: {0}'.format(number))
                if wait_for_element(self.driver, self.debug, 'usage-status-summary', 'class', 25):
                    print_debug(self.debug, 'found usage-status-summary')
                    return True
                else:
                    print_debug(self.debug, 'did not find usage-status-summary')
                    return False
            except NoSuchElementException:
                print_debug(self.debug, 'number "{0}" could no tbe found in portal'.format(number))
                return False
        else:
            return False

    def tarif_und_sim(self):
        """ tarif & sim-karte parsing """
        print_debug(self.debug, 'jump into tarif_und_sim')
        plandata_dic = {}

        if wait_for_element(self.driver, self.debug, 'tarifinfo', 'class', 25):
            soup = BeautifulSoup(self.driver.find_element_by_class_name('tarifinfo').get_attribute('innerHTML'), 'lxml')

            plandata_dic['tariff'] = soup.find('h2', attrs={'class':'h2 highlight'},).text.strip()
            print_debug(self.debug, 'plan-data tariff found: {0}'.format(plandata_dic['tariff']))
            try:
                plandata_dic['price'] = soup.find('div', attrs={'class':'price-single'},).text.strip()
                print_debug(self.debug, 'plan-data price found: {0}'.format(plandata_dic['price']))
            except AttributeError:
                print_debug(self.debug, 'plan-data price exception')

            dlitem = soup.find("dl")
            keys = dlitem.findAll('dt')
            values = dlitem.findAll('dd')

            cnt = 0
            for key in keys:
                plandata_dic[key.text.strip()] = values[cnt].text.strip()
                print_debug(self.debug, 'plan-data {0} found: {1}'.format(key.text.strip(), values[cnt].text.strip()))
                cnt += 1

        return plandata_dic

    def tarif_und_vertrag(self):
        """ tarif und vertrag section parsing """
        print_debug(self.debug, 'jump into tarif_und_vertrag')
        plandata_dic = {}

        if wait_for_element(self.driver, self.debug, 'composition', 'class', 25):
            print_debug(self.debug, 'item-collection')
            if self.debug:
                self.driver.save_screenshot('11-item-collection.png')

            try:
                link = self.driver.find_element_by_link_text('Mehr')
                link.click()
                print_debug(self.debug, 'Tarif und Vertrag Mehr click')
            except BaseException:
                print_debug(self.debug, 'Tarif und Vertrag Mehr failed')

            soup = BeautifulSoup(self.driver.find_element_by_tag_name('tariff-details').get_attribute('innerHTML'), 'lxml')
            spans = soup.findAll('span')
            try:
                plandata_dic['tariff'] = spans[0].text.strip()
                print_debug(self.debug, 'plan-data tariff found: {0}'.format(plandata_dic['tariff']))
            except BaseException:
                plandata_dic['tariff'] = 'unknown'
                print_debug(self.debug, 'plan-data tariff exception')
            try:
                plandata_dic['price'] = spans[1].text.strip() + ' ' + spans[2].text.strip()
                print_debug(self.debug, 'plan-data price found: {0}'.format(plandata_dic['price']))
            except BaseException:
                plandata_dic['price'] = 'unknown'
                print_debug(self.debug, 'plan-data price exception')

            items = soup.findAll('div', attrs={'class':'panel-dual-column-list-row bordered-row'})
            for item in items:
                values = item.findAll('p')
                try:
                    plandata_dic[values[0].text.strip()] = values[1].text.strip()
                    print_debug(self.debug, 'plan-data {0} found: {1}'.format(values[0].text.strip(), values[1].text.strip()))
                except BaseException:
                    pass

        return plandata_dic

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
        if wait_for_element(self.driver, self.debug, 'benutzername', 'id', 15):
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

        if wait_for_element(self.driver, self.debug, 'usageoverview', 'class', 15):
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
            return wait_for_element(self.driver, self.debug, 'usedvolume', 'class', 15)

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
