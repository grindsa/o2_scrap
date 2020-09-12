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
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

if sys.version_info > (3, 0):
    import importlib
    importlib.reload(sys)
else:
    reload(sys) # pylint: disable=E0602
    sys.setdefaultencoding('utf8') # pylint: disable=E1101

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
        elif etype == 'classpresent':
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@class="%s"]' % (ele)))
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

    def __init__(self, user=None, pwd=None, debug=False, headless=True, browser='firefox'):
        self.user = user
        self.pwd = pwd
        self.debug = debug
        self.headless = headless
        self.browser = browser.lower()

    def __enter__(self):
        """ Makes O2Mobile a Context Manager """
        if not self.driver:
            self._login()
            print_debug(self.debug, 'self._login() done')
        return self

    def __exit__(self, *args):
        """ Close the connection at the end of the context """
        print_debug(self.debug, 'we are in __exit__')
        self.logout()

    def _auth(self):
        """ authenticates towards an o2 portal by using a user password combination """
        print_debug(self.debug, 'O2mobile._auth()')
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
        print_debug(self.debug, 'O2mobile._auth() done')

    def _catch_modal_content(self):
        """ catch ads """
        print_debug(self.debug, 'O2mobile._catch_modal_content()')
        # close message asking to send ads
        if wait_for_element(self.driver, self.debug, 'modal-content', 'classpresent', 5):
            print_debug(self.debug, 'found modal-content')
            btn = self.driver.find_element_by_xpath('//div[@class="modal-header"]//button[@data-tracking-description="cms___close"]')
            btn.click()
        print_debug(self.debug, 'O2mobile._catch_modal_content() ended')

    def _catch_ads(self):
        """ catch ads """
        print_debug(self.debug, 'O2mobile._catch_ads()')

        # (driver, debug, ele, etype, timeout):
        if wait_for_element(self.driver, self.debug, 'Schließen', 'button', 15):
            # time.sleep(3)
            try:
                ads = self.driver.find_element_by_xpath('//button[@data-tracking-description="cms___Schließen")]')
                ads.click()
                print_debug(self.debug, 'pressed button to close overlay window')
            except BaseException:
                print_debug(self.debug, 'pressed button to close overlay window')
        else:
            print_debug(self.debug, 'found button schließen but could not press it')

    def _catch_cookies(self):
        """ catch cookies """
        print_debug(self.debug, "O2mobile._catch_cookies()")
        if wait_for_element(self.driver, self.debug, 'uc-btn-accept-banner', 'id', 5):
            print_debug(self.debug, 'found uc-btn-accept-banner')
            btn = self.driver.find_element_by_id("uc-btn-accept-banner")
            btn.click()
        else:
            if self.debug:
                self.driver.save_screenshot('06-cookie.png')
            print_debug(self.debug, 'cookie message wait done')

        print_debug(self.debug, 'O2mobile,_catch_cookies() ended')

    def _catch_optin(self):
        """ catch and accept optin """
        print_debug(self.debug, "O2mobile._catch_optin()")
        if wait_for_element(self.driver, self.debug, 'optinAcceptButton', 'id', 5):
            print_debug(self.debug, 'found optinAcceptButton')
            btn = self.driver.find_element_by_id("optinAcceptButton")
            btn.click()
        else:
            if self.debug:
                self.driver.save_screenshot('05-optin.png')
        print_debug(self.debug, 'O2mobile._catch_optin() ended')

    def _close_instance(self):
        """ closes an existing selenium web driver instance """
        print_debug(self.debug, "O2mobile._close_instance()")
        self.driver.close()
        # return None

    def _login(self):
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
        print_debug(self.debug, "O2mobile._login()")
        self.driver = self._new_instance()
        # open page
        try:
            # self.driver.get('https://login.o2online.de/auth/login?goto=https%3A%2F%2Fwww.o2online.de%2Fmein-o2%2F')
            self.driver.get('https://login.o2online.de/auth/login')
        except TimeoutException:
            print('timeout connecting to {0}'.format('https://login.o2online.de/auth/login'))
            sys.exit(0)

        if self.debug:
            self.driver.save_screenshot('00-login.png')

        # catch cookie-message
        self._catch_cookies()

        print_debug(self.debug, 'login-site fetched')
        self._auth()

        # catch login error
        try:
            error = self.driver.find_element_by_xpath('//div[contains(@class, "alert") and contains(@class, "alert-danger")]').text.strip()
        except NoSuchElementException:
            error = None
        print_debug(self.debug, 'login error handling completed')

        if error: # pylint: disable=R1705
            print('Login failed: {0}'.format(error))
            self._close_instance()
            sys.exit(0)
            return None
        else:

            # catch and confirm optin
            self._catch_optin()

            # optout from mailings
            self._catch_modal_content()

            try:
                link = self.driver.find_element_by_link_text('Verbrauch')
                link.click()
                print_debug(self.debug, 'Verbrauch click')
            except BaseException:
                print_debug(self.debug, 'Verbrauch failed')

            if self.debug:
                self.driver.save_screenshot('07-mv.png')

            if wait_for_element(self.driver, self.debug, 'usage-status-summary', 'class', 15): # pylint: disable=R1705
                print_debug(self.debug, 'usage-status-summary')
                if self.debug:
                    self.driver.save_screenshot('08-user-status-summary-succ.png')

                # get rid of this f**** advertisement pop-ups
                self._catch_ads()

                if self.debug:
                    self.driver.save_screenshot('09-end-login.png')
                print_debug(self.debug, 'we will return true now')
                return True
            else:
                print_debug(self.debug, 'usage-status-summary NOT found')
                self.driver.save_screenshot('08-user-status-summary-failed.png')
                self._close_instance()
                sys.exit(0)
                return False

    def _new_instance(self):
        """ initializes a new selenium web driver instance
        and returns a reference to the browser object for further processing """
        print_debug(self.debug, 'O2mobile._new_instance()')
        if self.browser == 'chrome':
            driver = self._new_chrome()
        else:
            driver = self._new_firefox()
        driver.set_window_size(1024, 768)
        driver.set_script_timeout(5)
        return driver

    def _new_firefox(self):
        """ creates a new firefox instance """
        print_debug(self.debug, 'O2mobile._new_firefox()')
        options = FirefoxOptions()
        if self.headless:
            print_debug(self.debug, 'activating headless mode')
            options.add_argument('-headless')
        driver = webdriver.Firefox(firefox_options=options)
        return driver

    def _new_chrome(self):
        """ creates a new chrome instance """
        print_debug(self.debug, 'O2mobile._new_chrome()')
        options = ChromeOptions()
        if self.headless:
            print_debug(self.debug, 'activating headless mode')
            options.add_argument('-headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(chrome_options=options)
        return driver

    def _switch_number(self, number):
        """ switch to a different phone number in o2 web portal
            args:
                number - phone number
            returns:
                True - in case the switch was successful
                False - in case switch failed
        """
        print_debug(self.debug, 'O2mobile._switch_number({0})'.format(number))
        ele = self.driver.find_element_by_class_name('side-nav-contract-choice-link')
        ele.click()
        print_debug(self.debug, 'side-nav-contract-choice-link clicked')
        if wait_for_element(self.driver, self.debug, 'side-nav-contract-choice-menu-items', 'class', 15):
            print_debug(self.debug, 'found side-nav-contract-choice-menu-items')
            # try:
            time.sleep(1)
            ele = self.driver.find_element_by_xpath("//span[contains(text(), '%s')]" % number)
            if self.debug:
                self.driver.save_screenshot('09-swnum.png')
            ele.click()
            print_debug(self.debug, 'found list-entry for number: {0}'.format(number))

            # get rid of this f**** advertisement pop-ups
            self._catch_ads()

            if wait_for_element(self.driver, self.debug, 'usage-info', 'class', 15): # pylint: disable=R1705
                print_debug(self.debug, 'found usage-info')
                return True
            else:
                print_debug(self.debug, 'did not find usage-info  but anyway')
                return True
        else:
            return False

    def _tarif_und_sim(self):
        """ tarif & sim-karte parsing """
        print_debug(self.debug, 'O2mobile._tarif_und_sim()')
        plandata_dic = {}

        if wait_for_element(self.driver, self.debug, 'tarifinfo', 'class', 15):
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

    def _tarif_und_vertrag(self):
        """ tarif und vertrag section parsing """
        print_debug(self.debug, 'O2mobile._tarif_und_vertrag()')
        plandata_dic = {}

        if wait_for_element(self.driver, self.debug, 'composition', 'class', 15):
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

    def get_bills(self):
        """ get list of bills per month """
        print_debug(self.debug, "O2mobile.get_bills()")
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
        print_debug(self.debug, "O2mobile.get_data_usage()")
        data_dic = {}
        if wait_for_element(self.driver, self.debug, 'usage', 'class', 15):
            print_debug(self.debug, 'usage')
            if self.debug:
                self.driver.save_screenshot('10-usage.png')

            # soup = BeautifulSoup(self.driver.find_element_by_tag_name('usage-monitor').get_attribute('innerHTML'), 'lxml')
            soup = BeautifulSoup(self.driver.find_element_by_class_name('usage-monitor').get_attribute('innerHTML'), 'lxml')

            # actual data usage
            usage_info = soup.find('div', attrs={'class':'usage-info'})

            try:
                usage_value = usage_info.find('div', attrs={'class':'usage-value'}).text.strip()
                data_dic['current'] = usage_value.replace('\n', ' ')
            except BaseException:
                data_dic['current'] = 'unknown'

            try:
                tmp_usage_max_value = usage_info.find('div', attrs={'class':'usage-max-value'})
                usage_max_value = tmp_usage_max_value.find('strong').text.strip()
                # re.sub(r'\s+', ' ', mystring).strip()
                data_dic['limit'] = re.sub(r'\s+', ' ', usage_max_value).strip()
            except BaseException:
                data_dic['limit'] = 'unknown'

            # estimation
            try:
                tmp_estimation = soup.find('cms-content', attrs={'cmssnippet':'/snippets/ecare/usage/ng/national-estimated-usage-text'})
                data_dic['estimation'] = tmp_estimation.find('strong').text.strip()
            except BaseException:
                pass

            data_dic['remaining'] = 'unknown'
        else:
            print_debug(self.debug, 'usage-status-summary NOT found')
            if self.debug:
                self.driver.save_screenshot('10-user-status-summary-failed.png')
        return data_dic

    def get_numbers(self):
        """ get phone numbers belonging to the contract-choice-link """
        print_debug(self.debug, "O2mobile.get_numbers()")
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
        """ get data consumption and contract details for a given number """
        print_debug(self.debug, 'O2mobile.get_overview({0})'.format(number))
        wait_for_element(self.driver, self.debug, 'navigation-label', 'class', 15)
        print_debug(self.debug, 'wait for navigation-label done')
        result = self._switch_number(number)
        print_debug(self.debug, 'sleep 2')
        time.sleep(2)
        number_dict = {}
        if result:
            # usage data
            try:
                link = self.driver.find_element_by_link_text('Verbrauch')
                link.click()
                number_dict['data-usage'] = self.get_data_usage()
            except BaseException:
                print_debug(self.debug, 'Verbrauch NOT found')
                link = self.driver.find_element_by_link_text('Mein O2 Übersicht')
                link.click()
                number_dict['data-usage'] = self.get_data_usage()

            # plan data
            try:
                link = self.driver.find_element_by_link_text('Tarif und Vertrag')
                link.click()
                number_dict['plan-data'] = self._tarif_und_vertrag()
            except BaseException:
                try:
                    link = self.driver.find_element_by_link_text('Tarif & SIM-Karte')
                    link.click()
                    number_dict['plan-data'] = self._tarif_und_sim()
                except BaseException:
                    print_debug(self.debug, 'panel-tariff-contract NOT found')
                    if self.debug:
                        self.driver.save_screenshot('11-panel-tariff-contract-failed.png')
        return number_dict

    def logout(self):
        """ logout method """
        print_debug(self.debug, 'O2mobile.logout()')
        link = self.driver.find_element_by_link_text('Mein O2')
        link.click()
        #ele = self.driver.find_element_by_xpath('//a[@href="https://login.o2online.de/auth/logout"]')
        #ele.click()
        print_debug(self.debug, 'looking for logout button')
        link = self.driver.find_element_by_link_text('Logout')
        link.click()
        self._close_instance()

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
        Makes O2dsl a Context Manager
        """
        if not self.driver:
            self._login()
        return self

    def __exit__(self, *args):
        """
        Close the connection at the end of the context
        """
        self.logout()

    def _auth(self):
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

    def _close_instance(self):
        """ closes an existing selenium web driver instance by using either PhantomJS or Mozilla

            args:
                self - self

            returns:
                None
        """
        if not self.debug:
            self.driver.close()
        # return None

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

    def _login(self):
        """ used to login towards an o2-online portal calling the following methods:

            args:
                self - self

            returns:
                Upon successfull login a reference to a selenium driver object will be returned.
                Otherwise the resturn code will be "False" and an error message get printed on STDOUT
        """
        self.driver = self._new_instance()
        # open page
        try:
            self.driver.get(self.base_url + 'sso/login')
        except TimeoutException:
            print('error connecting to {0}'.format(self.base_url + 'sso/login'))
            sys.exit(0)

        self._auth()

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
        self._close_instance()


    def _new_instance(self):
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
