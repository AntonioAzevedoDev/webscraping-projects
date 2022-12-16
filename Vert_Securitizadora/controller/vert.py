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
from Vert_Securitizadora.utils import utils
from Vert_Securitizadora.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Vert data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    body_data = browser.find_element(By.CSS_SELECTOR, '.p-datatable-tbody').find_elements(By.TAG_NAME, 'tr')
    aux_data = 0
    aux_series = 0
    pay_json = {}
    payload = {}
    len_total = 0
    len_items_page = 0
    scroll_home = 300
    len_items_page = len(body_data)
    while not WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.p-paginator-next'))).get_attribute('disabled') == '':
        while aux_data < len_items_page:
            while True:
                try:
                    body_data[aux_data].find_element(By.TAG_NAME, 'button').click()
                    sleep(1)
                    break
                except Exception as btn:
                    last_scroll_value = scroll_home
                    scroll_home += 300
                    browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_home})")
                    sleep(2)
                    body_data = browser.find_element(By.CSS_SELECTOR, '.p-datatable-tbody').find_elements(By.TAG_NAME,
                                                                                                          'tr')
                    continue

            try:

                header_text = ''

                internal_body_data = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.p-datatable-wrapper:nth-child(1) > table:nth-child(1) > tbody:nth-child(2)'))
                ).find_elements(By.TAG_NAME, 'tr')
                quant_series = len(internal_body_data)
                element = internal_body_data[0].find_element(By.TAG_NAME, 'td')
                element.click()
                sleep(5)
                try:
                    table_series = WebDriverWait(browser, 30).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.p-mb-3'))
                    )
                except Exception as tab:
                    table_series = []
                while True:
                    try:
                        sleep(2)
                        if table_series != []:
                            table_series = WebDriverWait(browser, 30).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.p-mb-3'))
                            ).find_elements(By.TAG_NAME, 'button')
                            len_total = len(table_series)
                        else:
                            len_total = 1

                        title = browser.find_element(By.CSS_SELECTOR, 'h1.main-title').text
                        serie_number = browser.find_element(By.CSS_SELECTOR, 'h2.main-title').text.split(' ')
                        serie_number = serie_number[0]

                        filepath = Path(
                            pc.CRA_PATH) / f"s-{utils.hashed(title)}-{datetime.now().strftime('%Y%m%d')}.json"
                        if not overwrite and filepath.exists():
                            print(f'Já existe: {title}')
                            sleep(2)
                            aux_data += 1
                            browser.find_element(By.CSS_SELECTOR, 'button.p-button:nth-child(1)').click()
                            sleep(6)
                            body_data = browser.find_element(By.CSS_SELECTOR, '.p-datatable-tbody').find_elements(
                                By.TAG_NAME, 'tr')
                            break

                        else:
                            payload_serie = {}
                            if table_series != []:
                                len_table = 0
                                if len(table_series) == 1:
                                    len_table = len(table_series)
                                else:
                                    len_table = len_total-1
                                while aux_series < len_table:
                                    serie_number = browser.find_element(By.CSS_SELECTOR, 'h2.main-title').text.split(' ')
                                    serie_number = serie_number[0]
                                    header_data = WebDriverWait(browser, 10).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, '#app > main:nth-child(2)'))
                                    )
                                    name_cra = WebDriverWait(browser, 10).until(
                                        EC.presence_of_element_located((By.TAG_NAME, 'h2'))
                                    ).text

                                    header_details = header_data.find_element(By.CSS_SELECTOR, 'div.p-flex-column:nth-child(1)').find_element(By.CSS_SELECTOR, '.chips-wrapper').find_elements(By.TAG_NAME, 'span')

                                    aux_header = 0
                                    while aux_header < len(header_details):
                                        if header_text == '':
                                            header_text = f'"{header_details[aux_header].text}":"{header_details[aux_header+1].text}"'
                                        else:
                                            header_text += f',"{header_details[aux_header].text}":"{header_details[aux_header + 1].text}"'
                                        aux_header += 2
                                    sleep(1)
                                    header_text = f'"Emissor":"{name_cra}",' + header_text
                                    table_text = ''

                                    table_body1 = browser.find_element(By.CLASS_NAME, 'p-card-body').find_elements(By.TAG_NAME, 'span')
                                    table_body2 = browser.find_element(By.CSS_SELECTOR, '.p-mb-1').find_element(By.CLASS_NAME, 'p-card-content').find_elements(By.TAG_NAME, 'span')
                                    table_carac = browser.find_element(By.CSS_SELECTOR, '.p-xl-8 > div:nth-child(2) > div:nth-child(2)').find_element(By.CLASS_NAME, 'p-card-body').find_element(By.CLASS_NAME, 'p-card-content').find_elements(By.TAG_NAME, 'span')
                                    sleep(1)
                                    table_text = get_data(table_text, table_body1)
                                    table_text = get_data(table_text, table_body2)
                                    table_text = get_data(table_text, table_carac)
                                    table_text = "{" + header_text + ' , ' + table_text + "}"
                                    sleep(1)
                                    docs = get_documents(browser)
                                    sleep(1)
                                    table_json = json.loads(table_text)
                                    #docs_json = json.loads(docs)
                                    payload_serie['Caracteristicas'] = table_json
                                    payload_serie['Documentos'] = docs
                                    payload[f'Serie {serie_number}'] = payload_serie

                                    scroll_value = 100
                                    while True:
                                        try:
                                            len_table = 0
                                            if len(table_series) == 1:
                                                len_table = len(table_series)
                                            else:
                                                len_table = len_total-1
                                            if aux_series >= len_table:
                                                break
                                            if scroll_value > 3000:
                                                scroll_value = 200
                                            last_scroll_value = scroll_value
                                            scroll_value += 300
                                            browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                                            try:
                                                table_series[aux_series].click()
                                            except Exception as tbcl:
                                                continue
                                            sleep(5)
                                            table_series = WebDriverWait(browser, 30).until(
                                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.p-mb-3'))
                                            ).find_elements(By.TAG_NAME, 'button')
                                            aux_series += 1

                                            break
                                        except Exception as cl:
                                            if check_banner(browser):
                                                table_series = WebDriverWait(browser, 30).until(
                                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.p-mb-3'))
                                                ).find_elements(By.TAG_NAME, 'button')
                                                continue
                                            else:
                                                sleep(1)
                                                table_series = WebDriverWait(browser, 30).until(
                                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.p-mb-3'))
                                                ).find_elements(By.TAG_NAME, 'button')
                                                continue
                                    sleep(5)
                            else:
                                serie_number = browser.find_element(By.CSS_SELECTOR, 'h2.main-title').text.split(' ')
                                serie_number = serie_number[0]
                                header_data = WebDriverWait(browser, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, '#app > main:nth-child(2)'))
                                )
                                name_cra = WebDriverWait(browser, 10).until(
                                    EC.presence_of_element_located((By.TAG_NAME, 'h2'))
                                ).text
                                header_details = header_data.find_element(By.CSS_SELECTOR,
                                                                          'div.p-flex-column:nth-child(1)').find_element(
                                    By.CSS_SELECTOR, '.chips-wrapper').find_elements(By.TAG_NAME, 'span')

                                aux_header = 0
                                while aux_header < len(header_details):
                                    if header_text == '':
                                        header_text = f'"{header_details[aux_header].text}":"{header_details[aux_header + 1].text}"'
                                    else:
                                        header_text += f',"{header_details[aux_header].text}":"{header_details[aux_header + 1].text}"'
                                    aux_header += 2
                                sleep(1)
                                header_text = f'"Emissor":"{name_cra}",' + header_text
                                table_text = ''

                                table_body1 = browser.find_element(By.CLASS_NAME, 'p-card-body').find_elements(
                                    By.TAG_NAME, 'span')
                                table_body2 = browser.find_element(By.CSS_SELECTOR, '.p-mb-1').find_element(
                                    By.CLASS_NAME, 'p-card-content').find_elements(By.TAG_NAME, 'span')
                                table_carac = browser.find_element(By.CSS_SELECTOR,
                                                                       '.p-xl-8 > div:nth-child(2) > div:nth-child(2)').find_element(
                                    By.CLASS_NAME, 'p-card-body').find_element(By.CLASS_NAME,
                                                                                   'p-card-content').find_elements(
                                    By.TAG_NAME, 'span')
                                sleep(1)
                                table_text = get_data(table_text, table_body1)
                                table_text = get_data(table_text, table_body2)
                                table_text = get_data(table_text, table_carac)
                                table_text = "{" + header_text + ' , ' + table_text + "}"
                                sleep(1)
                                docs = get_documents(browser)
                                sleep(1)
                                table_json = json.loads(table_text)
                                # docs_json = json.loads(docs)
                                payload_serie['Caracteristicas'] = table_json
                                payload_serie['Documentos'] = docs
                                payload[f'Serie {serie_number}'] = payload_serie
                            if payload == {}:
                                check_banner(browser)
                                continue
                            print(f"salvar {title}")
                            Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                            with open(filepath, "w", encoding="utf-8") as fp:
                                dump(payload, fp, ensure_ascii=False, indent=1)
                            payload = {}
                            aux_series = 0
                            pay_json = {}
                            browser.get(pc.CRA_URL)
                            sleep(5)
                            body_data = browser.find_element(By.CSS_SELECTOR, '.p-datatable-tbody').find_elements(
                                By.TAG_NAME, 'tr')
                            aux_data += 1
                            break


                    except Exception as inte:
                        try:
                            browser.find_element(By.CSS_SELECTOR, '.p-dialog-header-icon').click()
                            continue
                        except Exception as e:
                            check_banner(browser)
                            continue
            except Exception as app:
                print(app)
        sleep(1)
        next_page(browser)
        sleep(8)
        aux_data = 0
        body_data = browser.find_element(By.CSS_SELECTOR, '.p-datatable-tbody').find_elements(
            By.TAG_NAME, 'tr')


def get_data(table_text, table):
    try:
        aux_table = 0
        if len(table) % 2 == 0:
            while aux_table < len(table):
                if table_text == '':
                    table_text = f'"{table[aux_table].text}":"{table[aux_table + 1].text}"'
                else:
                    table_text += f',"{table[aux_table].text}":"{table[aux_table + 1].text}"'
                aux_table += 2

            return table_text
        else:
            while aux_table < len(table):
                if table[aux_table].text == 'Lastros' and table[aux_table + 2].text != 'Garantias':
                    list_lg = []
                    aux_lg = aux_table + 1
                    while table[aux_lg].text != 'Garantias':
                        list_lg.append(table[aux_lg].text)
                        aux_lg += 1
                        aux_table = aux_lg
                    table_text += f',"{table[aux_table].text}":"{list_lg}"'
                elif table[aux_table].text == 'Garantias' and table[aux_table + 2].text != 'Coordenador líder':
                    list_gc = []
                    aux_gc = aux_table + 1
                    while table[aux_gc].text != 'Coordenador líder':
                        list_gc.append(table[aux_gc].text)
                        aux_gc += 1
                        aux_table = aux_gc
                    table_text += f',"{table[aux_table].text}":"{list_gc}"'
                if table_text == '':
                    table_text = f'"{table[aux_table].text}":"{table[aux_table + 1].text}"'
                else:
                    table_text += f',"{table[aux_table].text}":"{table[aux_table + 1].text}"'
                aux_table += 2

            return table_text
    except Exception as gd:
        return table_text


def get_documents(browser):
    while True:
        try:
            sleep(1)
            doc_body = browser.find_element(By.ID, 'vert-docs').find_elements(By.CLASS_NAME, 'p-accordion-tab')
            text_doc = {}
            scroll_value = 1500
            for doc in doc_body:

                name_doc = doc.text
                while True:
                    try:
                        doc.find_element(By.TAG_NAME, 'a').click()
                        break
                    except Exception as cli:
                        try:
                            if check_banner(browser):
                                continue
                            else:
                                if scroll_value > 5000:
                                    scroll_value = 1000
                                last_scroll_value = scroll_value
                                scroll_value += 300
                                browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                                sleep(2)
                                doc_body = browser.find_element(By.ID, 'vert-docs').find_elements(By.CLASS_NAME,
                                                                                                  'p-accordion-tab')
                                sleep(2)
                                continue
                        except Exception as val:
                            last_scroll_value = scroll_value
                            scroll_value += 300
                            browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                            sleep(2)


                sleep(2)
                table_doc = doc.find_element(By.CLASS_NAME, 'p-datatable-wrapper').find_element(By.TAG_NAME, 'table')
                header_table = table_doc.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
                body_table = table_doc.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                item_data = []
                for data in body_table:
                    if 'Nenhum registro foi encontrado' in data.text:
                        text_doc[name_doc] = []
                    else:
                        if 'Preço Unitário' in name_doc:
                            data_splited = data.text.split(' ')
                            item_data.append({
                                header_table[0].text: data_splited[0],
                                header_table[1].text: data_splited[1],
                                header_table[2].text: data_splited[2],
                                header_table[3].text: data_splited[3],
                                header_table[4].text: data_splited[4],
                                header_table[5].text: data_splited[5],
                                header_table[6].text: data_splited[6],
                                header_table[7].text: data_splited[7],
                            })
                        elif 'Documentos da operação' in name_doc:
                            data_splited = data.find_elements(By.TAG_NAME, 'td')
                            item_data.append({
                                header_table[0].text: data_splited[0].text,
                                header_table[1].text: data_splited[1].text,
                                "Link": data.find_element(By.TAG_NAME,'a').get_attribute('href')
                            })

                        elif name_doc == 'Relatórios':
                            data_splited = data.find_elements(By.TAG_NAME, 'td')
                            item_data.append({
                                header_table[0].text: data_splited[0].text,
                                header_table[1].text: data_splited[1].text,
                                "Link": data.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            })

                        elif 'Comunicados' in name_doc:
                            data_splited = data.find_elements(By.TAG_NAME, 'td')
                            item_data.append({
                                header_table[0].text: data_splited[0].text,
                                header_table[1].text: data_splited[1].text,
                                "Link": data.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            })

                        elif 'Documentos da oferta' in name_doc:
                            data_splited = data.find_elements(By.TAG_NAME, 'td')
                            item_data.append({
                                header_table[0].text: data_splited[0].text,
                                header_table[1].text: data_splited[1].text,
                                "Link": data.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            })
                        elif 'Relatórios de rating' in name_doc:
                            data_splited = data.find_elements(By.TAG_NAME, 'td')
                            item_data.append({
                                header_table[0].text: data_splited[0].text,
                                header_table[1].text: data_splited[1].text,
                                "Link": data.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            })
                        else:
                            sleep(2)
                if item_data != []:
                    text_doc[name_doc] = item_data
                sleep(1)
                doc.find_element(By.TAG_NAME, 'a').click()
                sleep(1)
            return text_doc
        except Exception as do:
            check_banner(browser)
            if browser.find_element(By.CLASS_NAME, 'mdi mdi-minus-box-outline'):
                browser.find_element(By.CLASS_NAME,'mdi mdi-minus-box-outline').click()
            continue


def check_banner(browser):
    try:
        if WebDriverWait(browser, 2).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.p-dialog-header-icon'))):
            browser.find_element(By.CSS_SELECTOR, '.p-dialog-header-icon').click()
    except Exception as ban:
        print('')


def next_page(browser):
    try:
        scroll_value_next = 2000
        sleep(1)
        while not browser.find_element(By.CSS_SELECTOR, '.p-paginator-next').get_attribute('disabled') == '':
            try:
                browser.find_element(By.CSS_SELECTOR, '.p-paginator-next').click()
                return True
            except Exception as cl:
                last_scroll_value = scroll_value_next
                scroll_value_next += 100
                browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value_next})")
        return False
    except Exception as np:
        print(np)