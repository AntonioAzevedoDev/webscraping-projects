import hashlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep


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
        accept_btn_cookies = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#btnOkCookies'))
        )

        if accept_btn_cookies:
            print('aceitar cookies')
            accept_btn_cookies.click()
            sleep(1)
    except Exception as e:
        print('')


