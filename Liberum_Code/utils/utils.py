from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
from selenium.webdriver.support.ui import Select



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
        print(e)


def verify_pagination(browser):
    print('validando paginação')
    select = Select(browser.find_element(By.CSS_SELECTOR, 'select.form-control'))
    select.select_by_value('100')
    sleep(2)
    text = browser.find_element(By.CSS_SELECTOR,
                                 '#tbl-contact_info').text.split("de")
    text_splited = text[2].split(" ")
    total_pages = int(text_splited[1].replace('.', ''))/100
    total_pages = round(total_pages)+1
    return total_pages



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

