from datetime import datetime
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import SP_Global.data.pathandcredentials as path


def br_date(dte, sep='-', outfmt='%Y-%m-%d'):
    mes_int = {
        'jan': 1,
        'fev': 2,
        'mar': 3,
        'abr': 4,
        'mai': 5,
        'jun': 6,
        'jul': 7,
        'ago': 8,
        'set': 9,
        'out': 10,
        'nov': 11,
        'dez': 12
    }
    try:
        dd, mm, yy = dte.split(sep)
        _dte = datetime(
            int(yy),
            mes_int[mm[:3].lower()],
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
        accept_btn = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))
        )
        if accept_btn:
            print('aceitar cookies')
            accept_btn.click()
            sleep(1)
    except Exception as e:
        print('')

