from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains

def br_date(dte, sep=' ', outfmt='%Y-%m-%d'):
    mes_month = {
        'jan.': 1,
        'fev.': 2,
        'mar.': 3,
        'abr.': 4,
        'mai.': 5,
        'jun.': 6,
        'jul.': 7,
        'ago.': 8,
        'set.': 9,
        'out.': 10,
        'nov.': 11,
        'dez.': 12
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

def accept_terms_and_conditions(browser):
    try:
        action = ActionChains(browser)
        scrollbar = browser.find_element(By.CSS_SELECTOR, '#mdcloc-tc-text')
        scrollbar.click()
        for i in range(0, 3):
            action.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            sleep(1)

        checkbox = browser.find_element(By.CSS_SELECTOR, '#mdcloc-ua-checkbox')
        browser.execute_script("arguments[0].scrollIntoView();", checkbox)
        if checkbox:
            print('aceitar termos e condicoes')
            checkbox.click()
            button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mdcloc-ua-submit'))
            )
            button.click()
            sleep(1)
    except Exception as e:
        print(e)
