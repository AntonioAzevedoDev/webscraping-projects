from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Provincia.utils import utils
from Provincia.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Provincia data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(4)
    title = ''
    filepath = ''
    while True:
        try:
            browser.execute_script(f"window.scrollTo(0, 800)")
            sleep(2)
            iframe = browser.find_element(By.TAG_NAME, 'iframe')
            sleep(1)
            browser.switch_to.frame(iframe)
            sleep(1)
            table = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#dt-basic-example_wrapper"))
            ).find_element(By.TAG_NAME, 'table').find_elements(By.TAG_NAME, 'tr')
            aux_table = 0
            while aux_table < len(table):
                payload = {}
                details_data = table[aux_table].find_elements(By.TAG_NAME, 'td')
                if details_data == []:
                    aux_table += 1
                    continue
                for dd in details_data:
                    if dd.text == 'Detalhes':
                        header_text = ''
                        body_text = ''
                        doc_text = ''
                        dd.click()
                        sleep(2)
                        browser.switch_to.default_content()
                        title_cra = browser.current_url.split('=')[1]
                        title_cra = f'id - {title_cra}'
                        filepath = Path(
                            pc.CRA_PATH) / f"s-{utils.hashed(title_cra)}-{datetime.now().strftime('%Y%m%d')}.json"
                        if not overwrite and filepath.exists():
                            print(f'Já existe: {title_cra}')
                            sleep(2)
                            aux_table += 1
                            filepath = ''
                            continue

                        else:
                            payload_body = {}
                            header_data = browser.find_element(By.CSS_SELECTOR, '.padding-top-bottom-80').text.split('download\n')[1]
                            header_data = header_data.split('\n')
                            for hd in header_data:
                                if header_text == '':
                                    if ':' in hd:
                                        hd_splited = hd.split(':')
                                        hd_splited[1].replace(" ", "")
                                        header_text = f'"{hd_splited[0]}":"{hd_splited[1]}"'
                                    else:
                                        hd_splited = hd.split('EMISSÃO')
                                        emission = hd_splited[0]
                                        serie = hd_splited[1].split(' SÉRIE')
                                        if 'e' in serie[0]:
                                            serie[0] = utils.clear_text(serie[0])
                                            emission = utils.clear_text(emission)
                                            header_text = f'"Séries":"{serie[0]}","Emissão":"{emission.replace(" ","")}"'
                                            sleep(1)
                                        else:
                                            hd_splited[1].replace(" ", "")
                                            serie[0] = utils.clear_text(serie[0])
                                            emission = utils.clear_text(emission)
                                            header_text = f'"Série":"{serie[0].replace(" ","")}","Emissão":"{emission.replace(" ","")}"'
                                else:
                                    if ':' in hd:
                                        hd_splited = hd.split(': ')
                                        hd_splited[1].replace(" ", "")
                                        header_text += f',"{hd_splited[0]}":"{hd_splited[1]}"'
                                    else:
                                        header_text += f',"Série":"{hd}"'
                            header_text = "{" + header_text + "}"
                            header_json = json.loads(header_text)
                            payload["Dados da Oferta"] = header_json
                            try:
                                body_data = browser.find_element(By.CSS_SELECTOR, 'div.section:nth-child(3) > div:nth-child(2)')
                                body_details = body_data.find_elements(By.CSS_SELECTOR, '.col-xl-5')
                                body_list = []
                                if len(body_details) == 1:
                                    for details in body_details:
                                        title = details.find_element(By.TAG_NAME, 'h3').text
                                        if '(' in title:
                                            title = title.split(' (')
                                            serie_title = title[0]
                                            serie_title = serie_title.split('SÉRIE')
                                            serie_title = utils.clear_text(serie_title[0])
                                            class_title = title[1].replace(')', '').capitalize()
                                            title = f'"Série":"{serie_title}", "Classe":"{class_title}"'
                                        else:
                                            serie_title = title.split(' ')
                                            serie_title[0] = utils.clear_text(serie_title[0])
                                            title = f'"Série":"{serie_title[0]}"'
                                        details_splited = details.text.split('\n')
                                        for detail in details_splited:
                                            if ':' in detail:
                                                detail = detail.split(': ')
                                                if body_text == '':
                                                    body_text = title
                                                    detail[1].replace(" ", " ")
                                                    body_text += f',"{detail[0]}":"{detail[1]}"'
                                                else:
                                                    detail[1].replace(" ", " ")
                                                    body_text += f',"{detail[0]}":"{detail[1]}"'
                                        body_text = "{" + body_text + "}"
                                        body_json = json.loads(body_text)
                                        body_text = ''
                                        payload["Séries"] = body_json

                                else:
                                    aux_details = 0
                                    while aux_details < len(body_details) - 1:
                                        for details in body_details:
                                            title = details.find_element(By.TAG_NAME, 'h3').text
                                            if '(' in title:
                                                title = title.split(' (')
                                                serie_title = title[0]
                                                serie_title = serie_title.split('SÉRIE')
                                                serie_title = utils.clear_text(serie_title[0])
                                                class_title = title[1].replace(')', '').capitalize()
                                                title = f'"Série":"{serie_title}", "Classe":"{class_title}"'
                                            else:
                                                serie_title = title.split(' ')
                                                serie_title[0] = utils.clear_text(serie_title[0])
                                                title = f'"Série":"{serie_title[0]}"'
                                            details_splited = details.text.split('\n')
                                            for detail in details_splited:
                                                if ':' in detail:
                                                    detail = detail.split(': ')
                                                    if body_text == '':
                                                        body_text = title
                                                        detail[1].replace(" ", " ")
                                                        body_text += f',"{detail[0]}":"{detail[1]}"'
                                                    else:
                                                        detail[1].replace(" ", " ")
                                                        body_text += f',"{detail[0]}":"{detail[1]}"'
                                            body_text = "{" + body_text + "}"
                                            body_json = json.loads(body_text)
                                            body_text = ''
                                            body_list.append(body_json)
                                            aux_details += 1
                                if body_list != []:
                                    payload["Séries"] = body_list
                            except Exception as dt:
                                print(dt)
                            try:
                                #documentos
                                sleep(1)
                                select = browser.find_element(By.CSS_SELECTOR, '.nice-select')
                                select.click()
                                sleep(2)
                                documents_list = select.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
                                aux_document = 0
                                while aux_document < len(documents_list):
                                    if 'Selecione um anexo' in documents_list[aux_document].text:
                                        aux_document += 1
                                        continue
                                    else:
                                        doc_name = documents_list[aux_document].text
                                        documents_list[aux_document].click()
                                        sleep(3)
                                        browser.switch_to.window(browser.window_handles[1])
                                        doc_url = browser.current_url
                                        sleep(1)
                                        browser.close()
                                        browser.switch_to.window(browser.window_handles[0])
                                        sleep(1)
                                        if doc_text == '':
                                            doc_text = f'"{doc_name}":"{doc_url}"'
                                        else:
                                            doc_text += f',"{doc_name}":"{doc_url}"'
                                        select = browser.find_element(By.CSS_SELECTOR, '.nice-select')
                                        select.click()
                                        sleep(2)
                                        documents_list = select.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
                                        aux_document += 1
                                doc_text = "{" + doc_text + "}"
                                doc_json = json.loads(doc_text)
                                payload["Documentos"] = doc_json
                                sleep(1)
                            except Exception as d:
                                print(d)
                sleep(2)
                if filepath != '':
                    print(f'salvar')
                    Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    aux_table += 1
                browser.get(pc.CRA_URL)
                sleep(4)
                browser.execute_script(f"window.scrollTo(0, 800)")
                sleep(2)
                iframe = browser.find_element(By.TAG_NAME, 'iframe')
                sleep(1)
                browser.switch_to.frame(iframe)
                sleep(1)
                table = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#dt-basic-example_wrapper"))
                ).find_element(By.TAG_NAME, 'table').find_elements(By.TAG_NAME, 'tr')
            break
        except Exception as app:
            browser.switch_to.default_content()
            print(app)

