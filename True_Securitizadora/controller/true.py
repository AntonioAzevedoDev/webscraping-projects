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
from True_Securitizadora.utils import utils
from True_Securitizadora.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Travessia data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)

    scroll_value = 200
    payload = {}
    aux_cra = 0
    while True:
        try:
            body_items = browser.find_element(By.CSS_SELECTOR, '.items > div:nth-child(1)').find_elements(By.CLASS_NAME,
                                                                                                          'item')
            while aux_cra < len(body_items):
                name_item = body_items[aux_cra].find_element(By.TAG_NAME, 'b').text
                header_description = ''
                sleep(1)
                filepath = Path(
                    pc.CRA_PATH) / f"s-{utils.hashed(name_item)}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filepath.exists():
                    aux_cra += 1
                    continue

                else:
                    sleep(1)
                    try:
                        body_items[aux_cra].find_element(By.TAG_NAME, 'a').click()
                        sleep(2)
                    except Exception as cl:
                        if scroll_value >= 95000:
                            browser.execute_script(
                                f"window.scrollTo(0, -90000)")
                            scroll_value = 200
                            break
                        last_scroll_value = scroll_value
                        scroll_value += 200
                        browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                        sleep(1)
                        continue
                    try:
                        sleep(2)
                        browser.find_element(By.CSS_SELECTOR, 'button.btn:nth-child(6)').click()
                        sleep(2)
                        browser.find_element(By.CSS_SELECTOR, '#NOME').send_keys('a')
                        sleep(1)
                        browser.find_element(By.CSS_SELECTOR, '#EMAIL').send_keys('a')
                        sleep(1)
                        browser.find_element(By.CSS_SELECTOR, 'button.btn:nth-child(6)').click()
                    except Exception as no_banner:
                        print('Sem banner')
                    description_item = WebDriverWait(browser, 30).until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "div.header:nth-child(2) > div:nth-child(1)"))).text.split('\n')
                    description_item = description_item[1].split(' / ')
                    description_item_text = ''
                    aux_description = 0
                    while aux_description < len(description_item):
                        try:
                            new_item = description_item[aux_description].split(' ')
                            if description_item_text == '':
                                description_item_text = f'"{new_item[0]}":"{new_item[1]}"'
                            else:
                                description_item_text += f',"{new_item[0]}":"{new_item[1]}"'
                            aux_description += 1
                        except Exception as dit:
                            description_item[aux_description] = 'Código_CRA ' + description_item[aux_description]
                            continue

                    payload["Características"] = get_details(browser, description_item_text)
                    payload["Pagamentos"] = get_payment_data(browser)
                    payload = get_additional_data(browser, payload)
                    sleep(1)
                    print(f"salvar {name_item}")
                    Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    browser.get(pc.CRA_URL)
                    aux_cra += 1
                    sleep(5)
                    body_items = browser.find_element(By.CSS_SELECTOR, '.items > div:nth-child(1)').find_elements(By.CLASS_NAME, 'item')
            sleep(1)
            if aux_cra < len(body_items):
                continue
            else:
                break
        except Exception as app:
            print(app)


def get_details(browser, description_item_text):
    try:
        table_text = ''
        tables = browser.find_element(By.CSS_SELECTOR, 'div.col-md-6:nth-child(1)').find_elements(By.TAG_NAME, 'table')
        sleep(1)
        for table in tables:
            table_data = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
            for data in table_data:
                row_data = data.find_elements(By.TAG_NAME, 'td')
                if 'Emissão' in row_data[0].text or 'Série' in row_data[0].text:
                    continue
                else:
                    if table_text == '':
                        table_text = f'"{row_data[0].text}":"{row_data[1].text}"'
                    else:
                        table_text += f',"{row_data[0].text}":"{row_data[1].text}"'
        table_text = "{" + description_item_text + ',' + table_text + "}"
        table_json = json.loads(table_text)
        return table_json
    except Exception as details:
        table_json = []
        return table_json


def get_payment_data(browser):
    try:
        payment_text = ''
        tables = browser.find_element(By.CSS_SELECTOR, 'div.col-12:nth-child(2)').find_elements(By.TAG_NAME, 'table')
        sleep(1)
        for table in tables:
            table_data = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
            for data in table_data:
                row_data = data.find_elements(By.TAG_NAME, 'td')
                if payment_text == '':
                    payment_text = f'"{row_data[0].text}":"{row_data[1].text}"'
                else:
                    payment_text += f',"{row_data[0].text}":"{row_data[1].text}"'
        payment_text = "{" + payment_text + "}"
        table_json = json.loads(payment_text)
        return table_json
    except Exception as pay:
        table_json = []
        return table_json


def get_additional_data(browser, payload):
    buttons = browser.find_elements(By.CLASS_NAME, 'accordion')
    panels = browser.find_elements(By.CLASS_NAME, 'panel')
    aux_data = 0
    scroll_value = 1000
    doc_payload = []
    reports_payload = {}
    assemb_payload = []
    info_payload = []
    rating_payload = []
    anual_reports_payload = []
    demons_financ_payload = []
    fatos_payload = []
    demo_fin_ps_payload = []
    while aux_data < len(buttons):
        while True:
            try:
                buttons[aux_data].click()
                validator = WebDriverWait(buttons[aux_data], 30).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'btnMinus')))
                sleep(1)
                break
            except Exception as btn:
                if scroll_value >= 3000:
                    browser.execute_script(
                        f"window.scrollTo(0, -700)")
                    break
                last_scroll_value = scroll_value
                scroll_value += 200
                browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                sleep(1)
                continue
        table_doc = panels[aux_data].find_element(By.TAG_NAME, 'table')
        header_table = table_doc.find_elements(By.TAG_NAME, 'th')
        if buttons[aux_data].get_attribute('id') == 'documentos-da-operacao':
            try:
                doc_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        doc_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

            except Exception as doc_error:
                print(doc_error)
        elif buttons[aux_data].get_attribute('id') == 'relatorio-de-performance':
            try:
                reports_payload = {}
                if len(header_table) == 2:
                    data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                    for data in data_table:
                        if 'Nome do Arquivo Download' in data.text:
                            continue
                        else:
                            reports_pdf_payload = {}
                            rows = data.find_elements(By.TAG_NAME, 'td')
                            report_name = ''
                            while True:
                                try:
                                    rows[1].find_element(By.TAG_NAME, 'button').click()
                                    report_name = rows[0].text
                                    document = WebDriverWait(browser, 30).until(EC.element_to_be_clickable(
                                        (By.CSS_SELECTOR, 'div.modal:nth-child(5) > div:nth-child(1)')))
                                    break
                                except Exception as rcli:
                                    if scroll_value >= 5000:
                                        browser.execute_script(
                                            f"window.scrollTo(0, -700)")
                                        break
                                    last_scroll_value = scroll_value
                                    scroll_value += 200
                                    browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                                    sleep(1)
                                    continue
                            pdf_body = browser.find_element(By.CSS_SELECTOR, '.content').find_elements(By.TAG_NAME, 'table')
                            aux_pdf = 1
                            table_text_pdf = ''
                            for pd_table in pdf_body:

                                title_table = pd_table.find_element(By.CLASS_NAME, 'title').text
                                rows_pdf_table = pd_table.find_elements(By.TAG_NAME, 'tr')
                                for row_table in rows_pdf_table:
                                    row_data = row_table.find_elements(By.TAG_NAME, 'td')
                                    if title_table in row_data[0].text:
                                        continue
                                    else:
                                        if table_text_pdf == '':
                                            table_text_pdf = f'"{row_data[0].text}":"{row_data[1].text}"'
                                        else:
                                            table_text_pdf += f',"{row_data[0].text}":"{row_data[1].text}"'
                                table_text_pdf = "{" + table_text_pdf + "}"
                                json_text_pdf = json.loads(table_text_pdf)
                                if title_table in reports_payload:
                                    title_table = title_table + f" - {aux_pdf}"
                                reports_pdf_payload[title_table] = json_text_pdf

                                table_text_pdf = ''
                                aux_pdf += 1
                            reports_payload[report_name] = reports_pdf_payload
                            try:
                                browser.find_element(By.CSS_SELECTOR, 'button.close:nth-child(2)').click()
                            except Exception as bclose:
                                continue
                else:
                    try:
                        relat_anual_af_payload = []
                        assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                        data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                        for data in data_table:
                            if 'Data Nome do Arquivo Download' in data.text:
                                continue
                            else:
                                rows = data.find_elements(By.TAG_NAME, 'td')
                                data_doc = rows[0].text
                                nome = rows[1].text
                                relat_anual_af_payload.append({
                                    header_table[0].text: data_doc,
                                    header_table[1].text: nome,
                                    header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                                })
                                reports_payload["Relatório Anual"] = relat_anual_af_payload

                        sleep(1)
                    except Exception as relat_error:
                        print(relat_error)

            except Exception as doc_data_error:
                print(doc_data_error)

        elif buttons[aux_data].get_attribute('id') == 'assembleias':
            try:
                assemb_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        assemb_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as ass_error:
                print(ass_error)

        elif buttons[aux_data].get_attribute('id') == 'informe-mensal':
            try:
                info_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        info_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as inf_error:
                print(inf_error)

        elif buttons[aux_data].get_attribute('id') == 'rating':
            try:
                rating_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        rating_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as rat_error:
                print(rat_error)

        elif buttons[aux_data].get_attribute('id') == 'relatorios-anual-af':
            try:
                anual_reports_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        anual_reports_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as repo_error:
                print(repo_error)

        elif buttons[aux_data].get_attribute('id') == 'demonstracoes-financeiras':
            try:
                demons_financ_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        demons_financ_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as demo_error:
                print(demo_error)

        elif buttons[aux_data].get_attribute('id') == 'fatos-relevantes':
            try:
                fatos_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        fatos_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as fat_error:
                print(fat_error)

        elif buttons[aux_data].get_attribute('id') == 'demonstracoes-financeiras-do-ps':
            try:
                demo_fin_ps_payload = []
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        demo_fin_ps_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as demo_ps_error:
                print(demo_ps_error)

        elif buttons[aux_data].get_attribute('id') == 'documentos':
            try:
                assert len(header_table) == 3, f'expected 3 cols got {len(header_table)}'
                data_table = table_doc.find_elements(By.TAG_NAME, 'tr')
                for data in data_table:
                    if 'Data Nome do Arquivo Download' in data.text:
                        continue
                    else:
                        rows = data.find_elements(By.TAG_NAME, 'td')
                        data_doc = rows[0].text
                        nome = rows[1].text
                        doc_payload.append({
                            header_table[0].text: data_doc,
                            header_table[1].text: nome,
                            header_table[2].text: rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href'),
                        })

                sleep(1)
            except Exception as demo_ps_error:
                print(demo_ps_error)


        else:
            sleep(2)
        aux_data += 1
    payload["Documentos"] = doc_payload
    payload["Relatórios"] = reports_payload
    payload["Assembleias"] = assemb_payload
    payload["Informes"] = info_payload
    payload["Demonstrações Financeiras"] = demons_financ_payload
    payload["Demonstrações Financeiras PS"] = demo_fin_ps_payload
    payload["Ratings"] = rating_payload
    payload["Relatórios Anuais AF"] = anual_reports_payload
    payload["Fatos Relevantes"] = fatos_payload
    return payload
