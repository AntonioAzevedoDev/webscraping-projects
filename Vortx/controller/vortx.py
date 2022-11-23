from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import ast
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Vortx.utils import utils
from Vortx.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Dashboard data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    aux_pages = 1
    total_pages = utils.verify_pagination(browser)
    aux_row = 1
    column_value = 200
    number_files_saved = 0
    page_fixed = utils.get_page(browser)
    while aux_pages <= total_pages:
        page_now = utils.get_page(browser)
        while page_now != page_fixed:
            utils.next_page(browser)
            sleep(2)
            page_now = utils.get_page(browser)
        try:
            body_elements = [
                col
                for col in browser.find_element(By.CSS_SELECTOR, ".MuiTableBody-root").find_elements(By.TAG_NAME, "tr")
            ]
            while aux_row <= 10:
                for row in body_elements:
                    cra_data = []
                    payload = []
                    data_dict = ''
                    entry = ''
                    aux_entry = 0
                    header_file = ''
                    title = ''
                    title = browser.find_element(By.CSS_SELECTOR,
                                                 f'tr.MuiTableRow-root:nth-child({aux_row}) > td:nth-child(1) > a:nth-child(1) > div:nth-child(1)').text
                    if_code = browser.find_element(By.CSS_SELECTOR,
                                                 f'tr.MuiTableRow-root:nth-child({aux_row}) > td:nth-child(4) > a:nth-child(1) > div:nth-child(1)').text

                    if if_code == '':
                        if_code = 'empty'
                    filename = title + '-' + if_code
                    header = []
                    filepath = Path(
                        pc.CRA_PATH) / f"s-{utils.hashed(filename)}-{datetime.now().strftime('%Y%m%d')}.json"
                    if not overwrite and filepath.exists():
                        print(f'Já existe: {title}')
                        aux_row += 1
                        continue

                    else:
                        #Percorrer colunas
                        doc_payload = []
                        doc_assemb = []
                        doc_facts = []
                        doc_reports = []
                        doc_details = []
                        doc_obligations = []
                        while header == []:
                            try:
                                utils.expand_cra(browser, aux_row, column_value, page_now)
                                description = browser.find_element(By.CSS_SELECTOR, 'p.operacao-detalhe-info:nth-child(4)').text.split('ISIN')
                                isin_value = description[1]
                                sleep(1)
                                header = [
                                    col.text
                                    for col in
                                    browser.find_element(By.CSS_SELECTOR, ".operacao-detalhe-header-info").find_elements(
                                        By.TAG_NAME, "p")
                                ]
                                data_dict = f'"Emissora": "{title}","Emissão": "{header[1]}","Número IF": "{if_code}","ISIN": "{isin_value.strip()}"'

                                entry = WebDriverWait(browser, 30).until(EC.element_to_be_clickable(
                                    (By.CSS_SELECTOR, "section.operacao-detalhe:nth-child(3)"))).text.split('\n')
                                if entry == '':
                                    browser.refresh()
                                    sleep(3)
                                    page_fixed = page_now
                                    continue
                            except Exception as e:
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
                                    continue
                        try:
                            while aux_entry < len(entry):
                                if entry[aux_entry] == 'Garantias':
                                    while True:
                                        if entry[aux_entry+1] == '':
                                            cra_data.append({
                                                entry[aux_entry]: '-'
                                            })
                                            aux_entry += 2

                                        else:
                                            quant_data = 1
                                            cra_garantia = []

                                            while entry[aux_entry + quant_data] != 'Rating':
                                                cra_garantia.append(entry[aux_entry + quant_data])
                                                quant_data = quant_data + 1
                                            cra_data.append({
                                                entry[aux_entry]: entry[aux_entry + 1]
                                            })

                                            aux_entry += quant_data
                                            break
                                    data_dict += f',"{entry[aux_entry-(len(cra_garantia)+1)]}": "{cra_garantia}"'
                                else:
                                    if 'Preço Unitário' in entry[aux_entry]:
                                        aux_entry += 1
                                    else:
                                        if entry[aux_entry + 1] == '':
                                            cra_data.append({
                                                entry[aux_entry]: '-'
                                            })
                                            aux_entry += 2

                                        else:
                                            if '/' in entry[aux_entry+1]:
                                                entry[aux_entry + 1] = utils.format_date(entry[aux_entry + 1])
                                            cra_data.append({
                                                entry[aux_entry]: entry[aux_entry + 1]
                                            })
                                            data_dict += f',"{entry[aux_entry]}": "{entry[aux_entry + 1]}"'
                                            aux_entry += 2
                        except Exception as e:
                            print(f'While: {e}')
                        navigator = browser.find_element(By.CSS_SELECTOR,
                                                         '.operacao-detalhe-navbar > ul:nth-child(1)').find_elements(
                            By.TAG_NAME, 'li')
                        #Save Documents
                        save_documents(browser, doc_payload, navigator)
                        sleep(1)
                        #Save Assemblies
                        save_assemblies(browser, navigator, doc_assemb)
                        sleep(2)
                        #Save Facts
                        save_facts(browser, navigator, doc_facts)
                        sleep(2)
                        #Save Reports
                        save_reports(browser, navigator, doc_reports)
                        sleep(2)
                        #Save Details
                        save_details(browser, navigator, doc_details)
                        sleep(2)
                        #Save Obligations
                        save_obligations(browser, navigator, doc_obligations)
                        sleep(2)

                    if cra_data == []:
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
                            continue
                    else:
                        data_dict = "{"+data_dict+"}"
                        json_data = {}
                        try:
                            json_data = json.loads(data_dict)
                            if "[]" not in json_data['Garantias']:
                                json_data['Garantias'] = json_data['Garantias'].replace('[', '').replace(']', '')\
                                    .replace("'", "").replace(" ", "").split(',')
                            else:
                                json_data['Garantias'] = []
                            payload = json_data
                            payload["Documentos"] = doc_payload
                            payload["Assembleias"] = doc_assemb
                            payload["Fatos Relevantes"] = doc_facts
                            payload["Relatório do Ag. Fiduciário"] = doc_reports
                            payload["Detalhes"] = doc_details
                            payload["Obrigações"] = doc_obligations
                            print(f"salvar {title}")
                            Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                            with open(filepath, "w", encoding="utf-8") as fp:
                                dump(payload, fp, ensure_ascii=False, indent=1)
                            number_files_saved += 1
                            browser.close()
                            browser.switch_to.window(browser.window_handles[0])
                            aux_row += 1
                            column_value = 200
                            sleep(2)
                        except Exception as e:
                            print(f'CRA Data: {e}')

            #Next Page
            utils.next_page(browser)
            print(f'Página: {aux_pages + 1}')
            print(f'Number of files saved: {number_files_saved}')
            number_files_saved = 0
            aux_row = 1
            aux_pages += 1
            page_fixed = utils.get_page(browser)

        except Exception as f:
            if '10\n601-609' in page_now and aux_row == 10:
                break
            continue


def save_documents(browser, doc_payload, navigator):
    print("Save documents")
    while doc_payload == []:
        try:
            doc_data = []
            scroll_value = 100
            last_scroll_value = 200
            for nav in navigator:
                if "Documentos" in nav.text:
                    nav.click()
                    sleep(1)
                    aux = 1
                    docs = browser.find_element(By.CSS_SELECTOR, '.operacao-documentos').find_elements(By.CLASS_NAME,
                                                                                                       'operacao-documentos-tipo')
                    for doc in docs:
                        while aux <= len(docs):
                            try:
                                doc.click()
                                sleep(2)
                                if doc != '':
                                    document_elements = [
                                        col
                                        for col in
                                        browser.find_element(By.CSS_SELECTOR,
                                                             f'.operacao-documentos > div:nth-child({aux})').find_elements(
                                            By.TAG_NAME, "a")
                                    ]
                                    sleep(1)
                                    for document in document_elements:
                                        description = document.text
                                        if description == '':
                                            doc.click()
                                            sleep(1)
                                            break
                                        doc_data.append({"descrição": description, "url": document.get_attribute("href")})
                                        sleep(1)
                                    aux += 1
                                doc_payload.append({doc.text.replace('\n+', ''): doc_data})
                                doc_data = []
                                doc.click()
                                sleep(1)
                                browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                                break
                            except Exception as e:
                                if scroll_value >= 1500:
                                    browser.execute_script(
                                        f"window.scrollTo(0, -700)")
                                    break
                                last_scroll_value = scroll_value
                                scroll_value += 100
                                browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                                sleep(1)
                                continue
            browser.execute_script(f"window.scrollTo(0, -700)")
            sleep(2)
        except Exception as d:
            continue


def save_assemblies(browser, navigator, doc_assemb):
    print("Save assemblies")
    try:
        for nav in navigator:
            if "Assembleias" in nav.text:
                nav.click()
                sleep(1)
                ass_header = [
                    col.text
                    for col in
                    browser.find_element(By.CSS_SELECTOR,
                                             "#tabela-investidor").find_elements(
                        By.TAG_NAME, "th")
                ]
                assert len(ass_header) == 4, f"expected 4 cols, got {len(ass_header)}"
                ass_body = browser.find_element(By.CSS_SELECTOR,
                                               '#tabela-investidor > tbody:nth-child(2)').find_elements(By.TAG_NAME,
                                                                                                             'tr')
                for row in ass_body:
                    row_elements = row.find_elements(By.TAG_NAME, 'td')
                    doc_assemb.append({
                        ass_header[0]: row_elements[0].text,
                        ass_header[1]: utils.format_date(row_elements[1].text),
                        ass_header[2]: row_elements[2].text,
                        ass_header[3]: row_elements[3].find_element(By.TAG_NAME, 'a').get_attribute("href"),
                    })
    except Exception as ass:
        print(ass)


def save_facts(browser, navigator, doc_facts):
    print("Save facts")
    try:
        for nav in navigator:
            if "Fatos Relevantes" in nav.text:
                nav.click()
                sleep(1)

                fat_header = [
                    col.text
                    for col in
                    browser.find_element(By.CSS_SELECTOR,
                                            "#tabela-fatos").find_elements(
                        By.TAG_NAME, "th")
                ]
                assert len(fat_header) == 4, f"expected 4 cols, got {len(fat_header)}"
                try:
                    fat_body = browser.find_element(By.CSS_SELECTOR,
                                                        '#tabela-fatos > tbody:nth-child(2)').find_elements(By.TAG_NAME,
                                                                                                            'tr')
                except Exception as fat:
                    print(fat)
                    fat_body = []
                if fat_body != []:
                    for row in fat_body:
                        url_list = []
                        row_elements = row.find_elements(By.TAG_NAME, 'td')
                        row_url_list = row_elements[3].find_elements(By.TAG_NAME,
                                                                         'a')
                        if len(row_url_list) > 0:
                            for url in row_url_list:
                                url_list.append(url.get_attribute("href"))
                        doc_facts.append({
                            fat_header[0]: utils.format_date(row_elements[0].text),
                            fat_header[1]: row_elements[1].text,
                            fat_header[2]: row_elements[2].text,
                            fat_header[3]: url_list,
                        })
        sleep(2)
    except Exception as fact:
        print(fact)


def save_reports(browser, navigator, doc_reports):
    print("Save reports")
    try:
        for nav in navigator:
            if "Relatório do Ag. Fiduciário" in nav.text:
                nav.click()
                sleep(1)
                reports_header = [
                    col.text
                    for col in
                    browser.find_element(By.CSS_SELECTOR,
                                             "#tabela-investidor").find_elements(
                        By.TAG_NAME, "th")
                ]
                assert len(
                    reports_header) == 3, f"expected 3 cols, got {len(reports_header)}"
                reports_body = browser.find_element(By.CSS_SELECTOR,
                                                        '#tabela-investidor > tbody:nth-child(2)').find_elements(
                    By.TAG_NAME,
                    'tr')
                for row in reports_body:
                    row_elements = row.find_elements(By.TAG_NAME, 'td')
                    doc_reports.append({
                        reports_header[0]: row_elements[0].text,
                        reports_header[1]: row_elements[1].text,
                        "Url": row_elements[2].find_element(By.TAG_NAME, 'a').get_attribute(
                             "href"),
                    })
    except Exception as reports:
        print(reports)


def save_details(browser, navigator, doc_details):
    print("Save details")
    try:
        for nav in navigator:
            if "Detalhes" in nav.text:
                nav.click()
                sleep(1)
                try:
                    img_url = browser.find_element(By.CSS_SELECTOR, '.flowchart-img')
                    doc_details.append({"Url": img_url.get_attribute("src")})
                except Exception as image:
                    print(image)
        sleep(2)
    except Exception as details:
        print(details)


def save_obligations(browser, navigator, doc_obligations):
    print("Save obligations")
    try:
        for nav in navigator:
            if "Obrigações" in nav.text:
                nav.click()
                obli_aux = 0
                sleep(1)
                try:
                    obligations_data = browser.find_element(By.CSS_SELECTOR, ".obrigacoes-por-situacao").find_elements(
                        By.TAG_NAME, 'p')
                    while obli_aux < len(obligations_data):
                        doc_obligations.append({obligations_data[obli_aux].text: obligations_data[obli_aux + 1].text})
                        obli_aux += 2
                except Exception as obli_data:
                    print(obli_data)
    except Exception as obligations:
        print(obligations)
