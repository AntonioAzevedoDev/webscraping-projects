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
from Travessia.utils import utils
from Travessia.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Travessia data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    list_data = browser.find_element(By.CSS_SELECTOR, '.table_wrapper > table:nth-child(1)').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
    aux_data = 0
    scroll_value = 100
    payload = {}
    while aux_data < len(list_data):
        name_cra = ''
        url = ''
        if list_data[aux_data].text == '':
            aux_data += 1
            continue
        else:
            try:
                elem_cra = list_data[aux_data].find_elements(By.TAG_NAME, 'td')
                for ele in elem_cra:
                    if name_cra == '':
                        name_cra = ele.text
                    else:
                        name_cra += f',{ele.text}'
            except Exception as n:
                print(n)
            filepath = Path(
                pc.CRA_PATH) / f"s-{utils.hashed(name_cra)}-{datetime.now().strftime('%Y%m%d')}.json"
            if not overwrite and filepath.exists():
                aux_data += 1
                continue

            else:
                try:
                    url = list_data[aux_data].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    list_data[aux_data].find_element(By.TAG_NAME, 'a').click()
                except Exception as cl:
                    if scroll_value == 1000:
                        scroll_value = 100
                        continue
                    last_scroll_value = scroll_value
                    scroll_value += 100
                    browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                    sleep(2)
                    url = ''
                    continue
                sleep(3)
                try:
                    url_file = url
                    header_table = browser.find_element(By.CSS_SELECTOR, '.table-wrapper > table:nth-child(1)').find_elements(By.TAG_NAME, 'th')
                    header_data = browser.find_element(By.CSS_SELECTOR, '.table-wrapper > table:nth-child(1)').find_elements(By.TAG_NAME, 'td')
                    header_text = ''
                    assert len(header_table) == 5, f"expected 5 cols, got {len(header_table)}"
                    aux_header = 0
                    while aux_header < len(header_table):
                        if header_text == '':
                            header_text = f'"{header_table[aux_header].text.title()}":"{header_data[aux_header].text}"'
                        else:
                            header_text += f',"{header_table[aux_header].text.title()}":"{header_data[aux_header].text}"'
                        aux_header += 1
                    header_text = f'"Código do Emissor":"{utils.get_emissor_url(url_file)}",' + header_text
                    body_table = browser.find_element(By.CSS_SELECTOR, 'div.col-sm-6:nth-child(1) > ul:nth-child(1)').find_elements(By.TAG_NAME, 'li')
                    for bd in body_table:
                        bd_text = bd.text.split(': ')
                        header_text += f',"{bd_text[0]}":"{bd_text[1]}"'
                    header_text = "{" + header_text + "}"
                    header_json = json.loads(header_text)
                    payload = header_json

                    #get docs
                    payload = get_documents(browser, payload)
                    sleep(1)
                    print(f"Salvar {utils.get_emissor_url(url_file)}")
                    Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)

                    browser.get(pc.CRA_URL)
                    sleep(5)
                    aux_data += 1
                    list_data = browser.find_element(By.CSS_SELECTOR,'.table_wrapper > table:nth-child(1)').find_element(By.TAG_NAME,'tbody').find_elements(By.TAG_NAME, 'tr')

                except Exception as h:
                    print(h)


def get_documents(browser, payload):
    try:
        doc_body = browser.find_element(By.CSS_SELECTOR, '.docs').find_elements(By.TAG_NAME, 'li')
        doc_text = ''
        for doc in doc_body:
            doc_url = doc.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if doc_text == '':
                doc_text = f'"{doc.text}":"{doc_url}"'
            else:
                doc_text += f',"{doc.text}":"{doc_url}"'

        doc_text = "{" + doc_text + "}"
        doc_json = json.loads(doc_text)
        payload["Documentos"] = doc_json
        return payload
    except Exception as doc:
        payload["Documentos"] = []
        return payload
