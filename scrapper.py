import os
import zipfile
import string
from selenium import webdriver
from random import random, choice
from bs4 import BeautifulSoup
import time
from bs4.element import Tag
import requests
import json


def randomStringDigits():
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    rand_str = ''.join(choice(lettersAndDigits) for i in range(8))
    return rand_str


PROXY_USER = "jbyrd206"
PROXY_PASS = "Jcj7Uy9pc3yayISw_country-UnitedStates_session-{0}".format(
    randomStringDigits())
PROXY_HOST = "proxy.packetstream.io"
PROXY_PORT = "31112"

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        chrome_options=chrome_options)
    return driver


def get_soup():

    q = input("Give Query : \n")
    qp = "allintitle " + q
    query = qp.replace(" ", "+")
    driver = webdriver.Chrome(
        executable_path=r'C:/chromedriver/chromedriver.exe')
    google_url = f"https://www.google.com/search?q={query}" + "&num=" + str(5)
    # driver = get_chromedriver(use_proxy=True)
    driver.get(google_url)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    return soup, q


def get_result(soup):
    r_div = soup.find_all('div', attrs={'id': 'result-stats'})
    for i in r_div:
        x = i.text
    x = str(x)
    results = x.split(" ")
    result = results[1]
    result = result.replace(",", "")
    result = int(result)
    return result


def get_related_keyword(soup):
    r_p = soup.find_all('p', attrs={'class': 'nVcaUb'})
    kw = []
    for x in r_p:
        t = x.find('a')
        kw.append(t.text)
    return kw


def api_call(kw):
    data = {
        'country': 'us',
        'currency': 'USD',
        'dataSource': 'gkp',
        'kw[]': kw
    }
    my_headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 58e0fae7e0a411524a3e'
    }
    response = requests.post(
        'https://api.keywordseverywhere.com/v1/get_keyword_data', data=data, headers=my_headers)
    if response.status_code == 200:
        print('success\n\n')
        r = response.content.decode('utf-8')
        data = json.loads(r)
    else:
        print("An error occurred\n\n", response.content.decode('utf-8'))
    return data


def main():

    soup, q = get_soup()
    r = get_result(soup=soup)
    kw = get_related_keyword(soup=soup)
    kw.append(q)
    t = [q]
    data = api_call(kw=t)
    r_list = data['data']
    for x in r_list:
        no = x["vol"]
    result = {
        "keyword": q,
        "google results": r,
        "keyword_volume": no,
        "result": r/no
    }
    with open('result.txt', 'w') as file:
        file.write(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
