import hashlib
import os
from json import dump
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
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
            EC.presence_of_element_located((By.CSS_SELECTOR, '.MuiButton-containedSizeLarge > span:nth-child(1)'))
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
        footer = [
            col
            for col in browser.find_element(By.CSS_SELECTOR, ".MuiTableRow-footer").find_elements(By.TAG_NAME, "td")
        ]
        try:
            for col in footer:
                text = col.text.split("de")
                total_pages = int(text[1]) / 10
                if round(total_pages) <= total_pages:
                    total_pages = round(total_pages) + 1
                else:
                    total_pages = round(total_pages)
                return total_pages
        except Exception as e:
            print(f'Pagination: {e}')
    except Exception as e:
        print(f'Pagination: {e}')


def expand_cra(browser, aux, column_value, page_now):
    try:

        while True:
            try:
                browser.execute_script(f"window.scrollTo(0, {column_value})")
                sleep(2)
                element = browser.find_element(By.CSS_SELECTOR, f'tr.MuiTableRow-root:nth-child({aux}) > td:nth-child(1)')
                try:
                    ActionChains(browser).context_click(element).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
                    sleep(3)
                    browser.switch_to.window(browser.window_handles[1])
                except Exception as r:
                    if column_value > 643:
                        column_value = 643
                    else:
                        column_value *= 2
                    browser.execute_script(f"window.scrollTo(0, {column_value})")
                    continue
                sleep(3)
                break
            except Exception as e:
                try:
                    entry = browser.find_element(By.CSS_SELECTOR, "section.operacao-detalhe:nth-child(3)").text.split('\n')
                    if entry != '':
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                except Exception as e:

                    sleep(1)
                    if column_value > 643:
                        column_value = 643
                    else:
                        column_value *= 2
                    try:
                        browser.switch_to.window(browser.window_handles[1])
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        sleep(2)
                        continue
                    except Exception as e:
                        browser.refresh()
                        sleep(3)
                        page_fixed = page_now
                        break


    except Exception as e:
        print(f'Expand: {e}')




def get_page(browser):
    browser.find_element(By.CSS_SELECTOR, 'Body').send_keys(Keys.PAGE_DOWN)
    sleep(1)
    footer = [
        col
        for col in browser.find_element(By.CSS_SELECTOR, ".MuiTableRow-footer").find_elements(By.TAG_NAME, "td")
    ]
    try:
        for col in footer:
            text = col.text.split("de")
            page_now = text[0]
            return page_now
    except Exception as e:
        print(f'GetPage: {e}')


def next_page(browser):
    while True:
        try:
            browser.find_element(By.CSS_SELECTOR, 'Body').send_keys(Keys.PAGE_DOWN)
            sleep(1)
            button = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".jss14 > span:nth-child(4) > button:nth-child(1)")))
            sleep(1)
            button.click()
            sleep(1)
            browser.execute_script("window.scrollTo(0, -800)")
            sleep(1)
            break
        except Exception as e:
            continue


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