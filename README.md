# o2_scrap

o2_scrap is a python library to access the web portal of Telefonica O2 Germany to fetch 
- mobile data-usage of the phone numbers under a specific contract
- the mobile plan details
- the last 6 bills

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

To run o2_scrap on your system you need

* [Python] - (https://www.python.org)
* [Selenium] - (https://pypi.python.org/pypi/selenium) - Selenium Python Bindigs 
* [PhantomJs] - (http://http://phantomjs.org/) - PhantomJS is a headless WebKit scriptable via a JavaScript API  
* [geckodriver] - (https://github.com/mozilla/geckodriver) - Proxy for using W3C WebDriver-compatible clients to interact with Gecko-based browsers.
* [Beautiful Soup]  - (https://www.crummy.com/software/BeautifulSoup/) - a Python library for pulling data out of HTML and XML files.

Please make sure python and all the above modules had been installed successfully before you start any kind of testing.

### Installing

#### via Pypi
```
> pip install o2_scrap
```

#### manually for all users
1. download the archive and unpack it
2. enter the directory and run the setup script
```
> python setup.py install
```

#### manually for a single user
1. download the archive and unpack it
2. move the "o2_scrap" subfolder into the directory your script is located

### Usage

you need to import o2_scrap into your script
```
> from o2_scrap import O2mobile
``` 

create a new instance of DKBRobo and assing this object to a local variable
```
> O2M = O2mobile()
```

login to O2 Web portal

```
> o2b = O2M.login(<user-account>, <passoword>, debug (0 or 1))
```

this method will return a reference to a selenium browser object you need for later queries
```
> print(o2b)
<selenium.webdriver.firefox.webdriver.WebDriver (session="4a3393d4-b2fa-41c8-b32c-57a61a4b757c")>
```    

The method get_numbers() can be used to get the list of mobile numbers under the same contract 
```
numbers = O2M.get_numbers(o2b)
```
* o2b - the reference to the formerly created selenium object

The method returns a dictionary containing the mobile numbers and tariff name
```
> from pprint import pprint
> pprint(numbers)
{u'0176-1234567': u'O2 Blue Data S',
 u'0176-101010101': u'O2 Free M',
 u'0176-87654321': u'O2 Blue Basic',
 u'0176-12312345' Blue All-in L (2015)',
 u'0179-5513345': u'O2 Blue All-in S (2015)'}
```

To get the mobile data-usage and further plan details use the get_overview() method 
```
> data_dict = O2M.get_overview(o2b, <mobile-number>)
```
* o2b - the reference to the formerly created selenium object
* mobile-number - phone number to be queried (as obtained via get_numbers() method)

The method returns a dictionary in the following format
```
> from pprint import pprint
> pprint(data_dict)

{'data-usage': {'autoadjust': u'Datenautomatik deaktiviert',
                'current': '122 MB',
                'limit': u'2 GB',
                'remaining': u'15 Tag(e) verbleibend im Rechnungsmonat'},
 'plan-data': {u'K\xfcndigungsfrist:': u'3 Monat(e) zum Vertragsende',
               u'Verl\xe4ngerbar ab:': u'15.12.2017',
               u'Vertragsbeginn:': u'16.08.2016',
               u'Vertragsende:': u'15.08.2017',
               'price': u'19,99 \u20ac\nmonatlich',
               u'sp\xe4tester K\xfcndigungstermin:': u'15.05.2018',
               'tariff': u'O2 Blue All-in S (2015)'}}
```

To get the latest bills the method get_bills() has to be used.
```
bill_list = O2M.get_bills(o2b)
```
The method returns a list of bills in the follwoing format
```
> from pprint import pprint
> pprint(bill_list

[{'download': u'https://www.o2online.de/ecare/?0-1.ILinkListener-selfcarePanel-content-contentContainer-content-tabContent-content-mainBills-content-list-0-billDownloadPanel-billDocumentParts-0-downloadLink&intcmp=epo2p_quick-links-teaser_mein-o2-mein-verbrauch',
  'price': u'23,13€',
  'text': u'Aktuelle Rechnung vom 03.01.18'},
 {'download': u'https://www.o2online.de/ecare/?0-1.ILinkListener-selfcarePanel-content-contentContainer-content-tabContent-content-mainBills-content-list-1-billDownloadPanel-billDocumentParts-0-downloadLink&intcmp=epo2p_quick-links-teaser_mein-o2-mein-verbrauch',
  'price': u'56,95€',
  'text': u'Rechnung vom 03.12.17'},
 {'download': u'https://www.o2online.de/ecare/?0-1.ILinkListener-selfcarePanel-content-contentContainer-content-tabContent-content-mainBills-content-list-2-billDownloadPanel-billDocumentParts-0-downloadLink&intcmp=epo2p_quick-links-teaser_mein-o2-mein-verbrauch',
  'price': u'45,95€',
  'text': u'Rechnung vom 03.11.17'},
 {'download': u'https://www.o2online.de/ecare/?0-1.ILinkListener-selfcarePanel-content-contentContainer-content-tabContent-content-mainBills-content-list-3-billDownloadPanel-billDocumentParts-0-downloadLink&intcmp=epo2p_quick-links-teaser_mein-o2-mein-verbrauch',
  'price': u'23,39€',
  'text': u'Rechnung vom 04.10.17'},
 {'download': u'https://www.o2online.de/ecare/?0-1.ILinkListener-selfcarePanel-content-contentContainer-content-tabContent-content-mainBills-content-list-4-billDownloadPanel-billDocumentParts-0-downloadLink&intcmp=epo2p_quick-links-teaser_mein-o2-mein-verbrauch',
  'price': u'67,44€',
  'text': u'Rechnung vom 05.09.17'}]
```

## Further documentation
please check the [doc](https://github.com/grindsa/dkb-robo/tree/master/doc) folder of the project. You will find further documenation and an example scripts of all dkb-robo methods there.

## Contributing

Please read [CONTRIBUTING.md](https://github.com/grindsa/o2_scrap/blob/master/CONTRIBUTING.md) for details on my code of conduct, and the process for submitting pull requests.
Please note that I have a life besides programming. Thus, expect a delay in answering.

## Versioning

I use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/grindsa/dkb-robo/tags). 

## License

This project is licensed under the GPLv3 - see the [LICENSE.md](https://github.com/grindsa/o2_scrap/blob/master/LICENSE) file for details