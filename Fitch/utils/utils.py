import hashlib
import os
from json import dump
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
from selenium.webdriver.support.ui import Select

nods = lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%Y%m%d')
hashed = lambda x: hashlib.md5(f'{x}'.encode('utf-8')).hexdigest()

def br_date(dte, sep='-', outfmt='%Y-%m-%d'):
    mes_month = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }
    try:
        dd, mm, yy = dte.split(sep)
        _dte = datetime(
            int(yy),
            mes_month[mm.lower()],
            int(dd)
        ).strftime(outfmt)
    except:
        _dte = ''
    return _dte

def get_safe_setup(remote_url=None, headless=True):
    from selenium import webdriver
    # from seleniumwire import webdriver

    opts = webdriver.FirefoxOptions()
    opts.headless = headless
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-notifications")

    if remote_url is None:
        driver = webdriver.Firefox(options=opts)
    else:
        driver = webdriver.Remote(command_executor=remote_url, options=opts)

    # driver.implicitly_wait(10)

    return driver

def accept_cookies(browser):
    try:
        accept_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, '_evidon-accept-button'))
        )

        if accept_btn:
            print('aceitar cookies')
            accept_btn.click()
            sleep(1)
    except Exception as e:
        print('')


def verify_pagination(browser):
    print('validando paginação')
    try:
        select = Select(browser.find_element(By.CSS_SELECTOR, '.select-wrap > select:nth-child(1)'))
        select.select_by_value('100')
        sleep(2)
        radio = browser.find_element(By.CSS_SELECTOR,
                                     'div.rt-thead:nth-child(2) > div:nth-child(1) > div:nth-child(4) > input:nth-child(1)')
        browser.execute_script('arguments[0].click();', radio)
        browser.find_element(By.CSS_SELECTOR,
                             'div.rt-thead:nth-child(2) > div:nth-child(1) > div:nth-child(4) > input:nth-child(1)').send_keys(
            'Brazil')

        total = browser.find_element(By.CSS_SELECTOR, '.-totalPages').text
        page = browser.find_element(By.CSS_SELECTOR, '.-pageJump > input:nth-child(1)').get_attribute('value')
        if int(total) < int(page):
            btn = browser.find_element(By.CSS_SELECTOR, '.-next > button:nth-child(1)')
            browser.execute_script('arguments[0].click();', btn)
    except Exception as e:
        print('')

def return_header_splited(browser):
    header = [col.text for col in
              browser.find_element(By.CSS_SELECTOR, 'div.rt-thead:nth-child(1)').find_elements(By.CSS_SELECTOR,
                                                                                               'div.rt-thead:nth-child(1) > div:nth-child(1)')]
    header_splited = header[0].split("\n")
    return header_splited


def verify_pagination_entities(browser):
    print('validando paginação')
    sleep(1)
    total = browser.find_element(By.CSS_SELECTOR, '.search__results-count')
    total_splited = total.text.split(' ')
    total = int(total_splited[0])
    total_int = 0.0
    try:
        if total > 24:
            total_int = total/24
            total_int = round(total_int)+1
    except Exception as e:
        print('')
    return total_int


def return_url_splited(url):
    try:
        if url != '':
            url_splited = url.split('/entity/')
            url_splited_2 = url_splited[1].split('-')
            return url_splited_2
        else:
            return url
    except Exception as e:
        return ''




