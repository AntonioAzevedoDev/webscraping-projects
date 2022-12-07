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
from Opea.utils import utils
from Opea.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Ecoagro data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    aux_table = 0
    header_text = ''
    payload = {}
    scroll_value = 100
    try:
        table_data = browser.find_element(By.CSS_SELECTOR, '.styles_securityListContainer__8xiGP').find_elements(By.TAG_NAME, 'li')
        while aux_table < len(table_data):
            file_name = table_data[aux_table].find_element(By.CSS_SELECTOR,
                                                           f'.styles_securityListContainer__8xiGP > li:nth-child({aux_table+1}) > a:nth-child(1) > div:nth-child(1) > h5:nth-child(1) > span:nth-child(1)').text.replace("\n", " - ")
            filepath = Path(
                pc.CRA_PATH) / f"s-{utils.hashed(file_name)}-{datetime.now().strftime('%Y%m%d')}.json"
            if not overwrite and filepath.exists():
                print(f'Já existe: {file_name}')
                sleep(2)
                file_name = ''
                aux_table += 1
                continue

            else:

                while True:
                    try:
                        table_data[aux_table].click()
                        break
                    except Exception as tbc:
                        if scroll_value > 10000:
                            scroll_value = 200
                        last_scroll_value = scroll_value
                        scroll_value += 150
                        browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                        sleep(2)
                sleep(3)
                cra_name = browser.find_element(By.CSS_SELECTOR, '.text-truncate').text
                header_data = browser.find_element(By.CSS_SELECTOR, '.styles_propCardsContainer__1ag2n').find_elements(By.TAG_NAME, 'span')
                for hd in header_data:
                    if '.' in hd.text or 'Ativa' in hd.text:
                        continue
                    else:
                        hd_splited = hd.text.split(' ')
                        if header_text == '':
                            header_text = f'"{hd_splited[0]}":"{hd_splited[1]}"'
                        else:
                            header_text += f',"{hd_splited[0]}":"{hd_splited[1]}"'

                header_text = "{" + header_text + "}"
                header_json = json.loads(header_text)

                payload[cra_name] = header_json
                sleep(1)
                payload = get_caract(browser, payload)
                sleep(1)
                payload = get_monitoring_data(browser, payload)
                sleep(1)
                payload = get_download_documents(browser, payload)
                sleep(1)
                print(f'salvar {file_name}')
                Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as fp:
                    dump(payload, fp, ensure_ascii=False, indent=1)
                sleep(1)
                browser.get(pc.CRA_URL)
                sleep(5)
                table_data = browser.find_element(By.CSS_SELECTOR,
                                                  '.styles_securityListContainer__8xiGP').find_elements(By.TAG_NAME,
                                                                                                        'li')
                aux_table += 1
                header_text = ''
                payload = {}
    except Exception as app:
        print(app)


def get_caract(browser, payload):
    carac_text = ''
    browser.find_element(By.CSS_SELECTOR, '.styles_tabSelected__WzPrQ').click()
    sleep(1)
    name = browser.find_element(By.CSS_SELECTOR, '.styles_container__8xnZj').find_element(By.TAG_NAME, 'h2').text
    carac_data = browser.find_element(By.CSS_SELECTOR, '.styles_container__8xnZj').find_elements(By.CLASS_NAME,
                                                                                                 'styles_cell__H_X_j')
    for data in carac_data:
        data_text = data.text.split("\n")
        if carac_text == '':
            carac_text = f'"{data_text[0]}":"{data_text[1]}"'
        else:
            carac_text += f',"{data_text[0]}":"{data_text[1]}"'
    sleep(1)
    carac_text = "{" + carac_text + "}"
    carac_json = json.loads(carac_text)
    payload[name] = carac_json
    return payload


def get_monitoring_data(browser, payload):
    try:
        scroll_value = 1800
        monitoring_data = []
        browser.find_element(By.CSS_SELECTOR, '.styles_tabSelected__WzPrQ').click()
        sleep(3)
        name = browser.find_element(By.CSS_SELECTOR, '.styles_container__V5atD').find_element(By.TAG_NAME, 'h2').text
        header = browser.find_element(By.CSS_SELECTOR, '.styles_monitoringTable__Zj1DS > thead:nth-child(1)').find_elements(
            By.TAG_NAME, 'th')
        aux_carac = 0
        try:
            pag_tab = browser.find_element(By.CSS_SELECTOR, 'nav.MuiPagination-root:nth-child(1) > ul:nth-child(1)').find_elements(By.TAG_NAME, 'li')
        except Exception as pt:
            pag_tab = ['-', '-', '-', '-', '-']
        while True:
            if aux_carac == (len(pag_tab) - 4):
                break
            else:
                monitoring = browser.find_element(By.CSS_SELECTOR, '.styles_monitoringTable__Zj1DS')
                carac_data = browser.find_element(By.CSS_SELECTOR, '.styles_monitoringTable__Zj1DS > tbody:nth-child(2)').find_elements(By.TAG_NAME, 'tr')
                assert len(header) == 5, f'expected 5 cols, got {len(header)}'
                for data in carac_data:
                    url = data.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    data_details = data.find_elements(By.TAG_NAME, 'td')
                    monitoring_data.append({
                        header[0].text: data_details[0].text,
                        header[1].text: data_details[1].text,
                        header[2].text: data_details[2].text,
                        header[3].text: data_details[3].text,
                        header[4].text: url,
                    })

                while True:
                    try:
                        button_next = monitoring.find_element(By.CSS_SELECTOR,
                                                       'nav.MuiPagination-root:nth-child(1) > ul:nth-child(1) > li:nth-child(5) > button:nth-child(1)')
                    except Exception as nb:
                        break
                    try:
                        if button_next.get_attribute('disabled'):
                            break
                        else:
                            button_next.click()
                    except Exception as next:
                        if scroll_value > 3500:
                            scroll_value = 1800
                        last_scroll_value = scroll_value
                        scroll_value += 150
                        browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                        sleep(2)
                aux_carac += 1
        payload[name] = monitoring_data
        return payload
    except Exception as mon:
        payload["Monitoramentos"] = {}
        return payload


def get_download_documents(browser, payload):
    try:
        doc_text = ''
        browser.find_element(By.CSS_SELECTOR, '.styles_tabSelected__WzPrQ').click()
        sleep(2)
        name = browser.find_element(By.CSS_SELECTOR, '.styles_container__V5X0M').find_element(By.TAG_NAME, 'h2').text
        doc_data = browser.find_element(By.CSS_SELECTOR, '.styles_grid__0ewxg').find_elements(By.TAG_NAME, 'li')
        aux_name_doc = 1
        for doc in doc_data:
            if doc.text == '':
                continue
            else:
                url = doc.find_element(By.TAG_NAME, 'a').get_attribute('href')
                name_doc = doc.find_element(By.CLASS_NAME, 'styles_titleLine__V1X_t ').text
                if doc_text == '':
                    doc_text = f'"{name_doc}":"{url}"'
                else:
                    if name_doc in doc_text:
                        name_doc = name_doc + f' - {aux_name_doc}'
                    doc_text += f',"{name_doc}":"{url}"'
                    aux_name_doc += 1
        sleep(1)
        doc_text = "{" + doc_text + "}"
        doc_json = json.loads(doc_text)
        payload[name] = doc_json
        return payload
    except Exception as d:
        payload["Downloads da Operação"] = {}
        return payload
