from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Barisec.utils import utils
from Barisec.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Barisec data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    aux = 1
    scroll_value = 100
    last_scroll_value = 200
    button_next = browser.find_element(By.CSS_SELECTOR, '.next > a:nth-child(1)')
    next_validator = True
    aux_page = 1
    while next_validator:
        if aux > 20:
            try:
                if aux_page > 7:
                    next_validator = False
                    break
                else:
                    browser.execute_script(f"window.scrollTo(831,2500)")
                    sleep(2)
                    button_next = browser.find_element(By.CSS_SELECTOR, '.next > a:nth-child(1)')
                    sleep(1)
                    #ActionChains(browser).move_to_element(button_next).perform()
                    button_next.click()
                    aux_page += 1
                    aux = 1
            except Exception as vali:
                continue
        while True:
            try:
                try:
                    active = browser.find_element(By.CSS_SELECTOR, f'div.EmissionsPagination__EmissionCardItem-sc-n54vpl-2:nth-child({aux}) > div:nth-child(1) > div:nth-child(2) > p:nth-child(2)')
                except Exception as ac:
                    if aux < 21:
                        next_validator = False
                        break
                    else:
                        next_validator = True
                        break
                filepath = Path(
                    pc.CRA_PATH) / f"s-{utils.hashed(active.text)}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filepath.exists():
                    print(f'Já existe: {active.text}')
                    sleep(2)
                    aux += 1
                    continue

                else:
                    try:
                        title = active.text
                        list_cra = WebDriverWait(browser, 999).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.EmissionsPagination__EmissionsPaginationContainer-sc-n54vpl-1'))
                        )
                        cra = list_cra.find_element(By.CSS_SELECTOR, f'div.EmissionsPagination__EmissionCardItem-sc-n54vpl-2:nth-child({aux})')
                        button = cra.find_element(By.CSS_SELECTOR, f'div.EmissionsPagination__EmissionCardItem-sc-n54vpl-2:nth-child({aux}) > div:nth-child(1) > a:nth-child(7) > button:nth-child(1)')
                        sleep(2)
                        ActionChains(browser).context_click(button).key_down(Keys.CONTROL).click(button).key_up(
                            Keys.CONTROL).perform()
                        sleep(3)
                        browser.switch_to.window(browser.window_handles[1])
                        sleep(2)
                        table_data = browser.find_element(By.CSS_SELECTOR, '.EmissionDetailedCard__EmissionDetailedCardTableContent-sc-1ueuiis-4')
                        data_splited = table_data.text.split("\n")
                        aux_data = 1
                        row_values = ''
                        row_data = []
                        while True:
                            try:
                                if aux_data == 5:
                                    aux_data += 1
                                row_data.append(browser.find_element(By.CSS_SELECTOR, f'div.EmissionDetailedCard__EmissionDetailedCardTableRow-sc-1ueuiis-5:nth-child({aux_data})'))
                                aux_data += 1
                            except Exception as ex:
                                break
                        aux_data = 0
                        text_payload = ''
                        while aux_data < len(row_data):
                            try:
                                text = row_data[aux_data].text.split('\n')
                                if text_payload == '':
                                    text_payload = f'"{text[0]}": "{text[1]}"'
                                    aux_data += 1
                                else:
                                    text_payload += f',"{text[0]}": "{text[1]}"'
                                    aux_data += 1
                            except Exception as empty:
                                text = row_data[aux_data].text.split('\n')
                                if text_payload == '':
                                    text_payload = f'"{text[0]}": "-"'
                                    aux_data += 1
                                else:
                                    text_payload += f',"{text[0]}": "-"'
                                    aux_data += 1
                        text_payload = "{" + text_payload + "}"

                        text_document = get_documents(browser)
                        text_report = get_reports(browser)
                        document_json = json.loads(text_document)
                        reports_json = json.loads(text_report)
                        text_json = json.loads(text_payload)
                        payload = text_json
                        payload["Documentos"] = document_json
                        payload["Relatórios"] = reports_json
                        print(f'salvar {title}')
                        Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                        with open(filepath, "w", encoding="utf-8") as fp:
                            dump(payload, fp, ensure_ascii=False, indent=1)
                        aux += 1
                        sleep(2)
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        sleep(3)
                    except Exception as save:
                        if scroll_value > 2500:
                            scroll_value = 200
                        last_scroll_value = scroll_value
                        scroll_value += 50
                        browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                        sleep(1)
                        continue
            except Exception as e:
                #print(e)
                break


def get_documents(browser):
    try:
        text_document = ''
        aux_data = 1
        doc_body = browser.find_element(By.CSS_SELECTOR,
                                        '.EmissionDetailedCard__EmissionDetailedCardDocumentsContent-sc-1ueuiis-8')
        while True:
            try:
                doc = doc_body.find_element(By.CSS_SELECTOR,
                                            f'div.EmissionDetailedCard__EmissionDetailedCardDocumentsCardContainer-sc-1ueuiis-9:nth-child({aux_data}) > div:nth-child(1)')
                url = doc.find_element(By.TAG_NAME, 'a').get_attribute('href')
                text_data = doc.find_elements(By.TAG_NAME, 'p')
                doc_name = ''
                for text in text_data:
                    if text.text == 'PDF':
                        continue
                    else:
                        doc_name = text
                        break
                if text_document != '':
                    text_document += f',"{doc_name.text}": "{url}"'

                else:
                    text_document += f'"{doc_name.text}": "{url}"'
                aux_data += 1
            except Exception as doc:
                break
        text_document = "{" + text_document + "}"
        return text_document
    except Exception as fail:
        text_document = '{}'
        return text_document


def get_reports(browser):
    try:
        text_report = ''
        aux_data = 1
        report_body = browser.find_element(By.CSS_SELECTOR,
                                        '.EmissionDetailedCardPerformanceReport__EmissionDetailedCardPerformanceReportContent-sc-qpq911-0')
        while True:
            try:
                report = report_body.find_element(By.CSS_SELECTOR,
                                            f'div.EmissionDetailedCardPerformanceReport__EmissionDetailedCardPerformanceReportCard-sc-qpq911-1:nth-child({aux_data})')
                url = report.find_element(By.TAG_NAME, 'a').get_attribute('href')
                text_data = report.find_elements(By.TAG_NAME, 'p')
                report_name = ''
                for text in text_data:
                    if text.text == 'PDF':
                        continue
                    else:
                        report_name = text
                        break
                if text_report != '':
                    text_report += f',"{report_name.text}": "{url}"'

                else:
                    text_report += f'"{report_name.text}": "{url}"'
                aux_data += 1
            except Exception as rep:
                break
        text_report = "{" + text_report + "}"
        return text_report
    except Exception as fail:
        text_report = '{}'
        return text_report
