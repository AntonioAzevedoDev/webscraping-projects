import re
from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import ast
import json
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains, Keys
from Ecoagro.utils import utils
from Ecoagro.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Ecoagro data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    title = ''
    aux_pages = 1
    scroll_value = 100
    aux_cra = 1
    try:
        button_next = browser.find_element(By.CSS_SELECTOR, '.next > a:nth-child(1)')
        while WebDriverWait(browser, 30).until(
                    EC.element_to_be_clickable(button_next)):
            cra_list = browser.find_element(By.CSS_SELECTOR, '.emissao-list').find_elements(By.TAG_NAME, 'li')
            for cra in cra_list:
                if 'OPERAÇÃO' in cra.text:
                    continue
                else:

                    cra_details_id = cra.find_elements(By.CLASS_NAME, 'column')
                    aux_detail = 0
                    for detail in cra_details_id:
                        if aux_detail == 3:
                            break
                        else:
                            if title != '':
                                title += '-' + detail.text
                            else:
                                title = detail.text
                    filepath = Path(
                        pc.CRA_PATH) / f"s-{utils.hashed(title)}-{datetime.now().strftime('%Y%m%d')}.json"
                    if not overwrite and filepath.exists():
                        print(f'Já existe: {title}')
                        sleep(2)
                        title = ''
                        continue

                    else:
                        try:
                            aux_series = 1
                            cra_text = ''
                            doc_text = ''
                            text_payload = ''
                            while True:
                                try:
                                    ActionChains(browser).context_click(cra).key_down(Keys.CONTROL).click(cra).key_up(
                                        Keys.CONTROL).perform()
                                    break
                                except Exception as cl:
                                    if scroll_value == 1000:
                                        scroll_value = 100
                                        continue
                                    last_scroll_value = scroll_value
                                    scroll_value += 100
                                    browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                                    sleep(2)
                                    continue
                            sleep(3)
                            browser.switch_to.window(browser.window_handles[1])
                            sleep(2)
                            try:
                                series = Select(browser.find_element(By.CSS_SELECTOR, '#series'))
                                quant_series = len(series.options)
                            except Exception as s:
                                series = browser.find_element(By.CSS_SELECTOR, '.serie')
                                quant_series = 1
                            if aux_series == quant_series:
                                text_payload = get_data(browser, cra_text, doc_text, text_payload)
                                sleep(1)
                                print(f'salvar {title}')
                                Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                                with open(filepath, "w", encoding="utf-8") as fp:
                                    dump(text_payload, fp, ensure_ascii=False, indent=1)
                                sleep(1)
                                text_data = ''
                                title = ''
                                browser.close()
                                browser.switch_to.window(browser.window_handles[0])
                                sleep(2)
                        except Exception as tp:
                            print(tp)
                        else:
                            try:
                                payload = {}
                                while aux_series <= quant_series:
                                    text_payload = get_data(browser, cra_text, doc_text, text_payload)
                                    payload[f"Série {aux_series}"] = text_payload
                                    aux_series += 1
                                    text_payload = ''
                                    pattern = re.compile(f'{aux_series}')
                                    for option in series.options:
                                        value = option.get_attribute('text')
                                        if pattern.search(value):
                                            option.click()
                                            sleep(3)
                                            series = Select(browser.find_element(By.CSS_SELECTOR, '#series'))
                                            break

                                print(f'salvar {title}')
                                Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                                with open(filepath, "w", encoding="utf-8") as fp:
                                    dump(payload, fp, ensure_ascii=False, indent=1)
                                sleep(1)
                                text_data = ''
                                title = ''
                                browser.close()
                                browser.switch_to.window(browser.window_handles[0])
                                sleep(2)
                            except Exception as pay:
                                print(pay)
            while True:
                try:
                    button_next.click()
                    break
                except Exception as bu:
                    last_scroll_value = scroll_value
                    scroll_value += 150
                    browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                    sleep(2)

            sleep(3)
            scroll_value = 100
            button_next = browser.find_element(By.CSS_SELECTOR, '.next > a:nth-child(1)')
    except Exception as app:
        print(app)


def get_data(browser, cra_text, doc_text, text_payload):
    try:
        cra_body = browser.find_element(By.CSS_SELECTOR, 'div.container:nth-child(2)').find_elements(By.TAG_NAME, 'section')
        for cr in cra_body:
            if 'Cadastre-se e acompanhe as emissões' in cr.text:
                continue
            elif 'Características' in cr.text:
                items = cr.find_elements(By.CLASS_NAME, 'item')
                name = cr.find_element(By.TAG_NAME, 'p').text
                for item in items:
                    item_details = item.find_elements(By.TAG_NAME, 'p')
                    if cra_text == '' and item_details[1].text != '':
                        cra_text = f'"{item_details[0].text}":"{item_details[1].text}"'
                    elif item_details[1].text == '':
                        if cra_text == '':
                            cra_text = f'"{item_details[0].text}":"-"'
                        else:
                            cra_text += f',"{item_details[0].text}":"-"'
                    else:
                        cra_text += f',"{item_details[0].text}":"{item_details[1].text}"'

                sleep(1)
                if text_payload == '':
                    cra_text = '{' + f'"{name}":' + "{" + cra_text + "}}"
                    cra_json = json.loads(cra_text)
                    text_payload = cra_json
                else:
                    cra_text = "{" + cra_text + "}"
                    cra_json = json.loads(cra_text)
                    text_payload[name] = cra_json
                cra_text = ''
                sleep(1)

            elif 'Documentos da Oferta' in cr.text:
                doc_list = cr.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
                for doc in doc_list:
                    doc_name = doc.text
                    url_list = browser.find_element(By.CSS_SELECTOR, '.content-list').find_elements(By.TAG_NAME, 'li')
                    if len(url_list) == 1:
                        if doc_text == '':
                            doc_text = f'"{doc_name}":"{url_list[0].find_element(By.TAG_NAME, "a").get_attribute("href")}"'
                        else:
                            doc_text += f',"{doc_name}":"{url_list[0].find_element(By.TAG_NAME, "a").get_attribute("href")}"'
                    else:
                        text_url_list = []
                        for url in url_list:
                            text_url_list.append(url.find_element(By.TAG_NAME, "a").get_attribute("href"))
                        if doc_text == '':
                            doc_text = f'"{doc_name}":"{text_url_list}"'
                        else:
                            doc_text += f',"{doc_name}":"{text_url_list}"'
                        sleep(1)

                doc_text = "{" + doc_text + "}"
                doc_json = json.loads(doc_text)
                text_payload["Documentos da Oferta"] = doc_json
                sleep(1)
            else:
                break
        return text_payload
    except Exception as get:
        print(get)
