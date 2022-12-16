import hashlib
import os
from json import dump
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver import Keys, ActionChains


nods = lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%Y%m%d')
hashed = lambda x: hashlib.md5(f'{x}'.encode('utf-8')).hexdigest()


def get_safe_setup(remote_url=None, headless=True):

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

    return driver


def accept_cookies(browser):
    try:
        accept_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.vert-btn-dlg:nth-child(2)'))
        )

        accept_btn2 = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#adopt-accept-all-button'))
        )

        if accept_btn:
            print('aceitar cookies')
            accept_btn.click()
            sleep(1)

        if accept_btn:
            accept_btn2.click()
            sleep(1)
    except Exception as e:
        print('')


def format_date(dte, sep='/', outfmt='%Y-%m-%d'):

    try:
        dd, mm, yy = dte.split(sep)
        _dte = datetime(
            int(yy),
            int(mm),
            int(dd)
        ).strftime(outfmt)
    except:
        _dte = ''
    return _dte