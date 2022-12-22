from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains, Keys
from Octante.utils import utils
from Octante.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Octante data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    filepath = ''
    aux_data = 0
    scroll(browser)
    sleep(2)
    table_data = browser.find_elements(By.CLASS_NAME, 'item-link-wrapper')
    sleep(1)
    total_itens = len(table_data)
    scroll_value = 200
    aux_validator = 0
    last_scroll_value = 300
    while aux_data < total_itens:
        try:
            payload_text = {}
            image_data = ''
            details_payload_text = ''
            doc_text = ''
            element_data = table_data[aux_data].find_elements(By.TAG_NAME, 'div')
            validator = ''

            while True:
                try:
                    hover = ActionChains(browser)
                    hover.move_to_element(element_data[2])
                    sleep(2)
                    if aux_validator > 15:
                        browser.execute_script(f"window.scrollTo(0, {last_scroll_value})")
                        sleep(2)
                        last_scroll_value += 200
                    hover.click(element_data[2])
                    sleep(1)
                    hover.perform()
                    sleep(1)
                    validator = WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'section'))
                    )
                    if validator == '':
                        last_scroll_value = scroll_value
                        scroll_value += 200
                        browser.execute_script(f"window.scrollTo(0, {scroll_value})")
                        sleep(1)
                        continue
                    else:
                        aux_validator += 1
                        break
                except Exception as ex:
                    while scroll_value < 1000:
                        try:
                            last_scroll_value = scroll_value
                            scroll_value += 200
                            browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
                            sleep(1)
                            continue
                        except Exception as scro:
                            print(scro)
            filename = ''
            sleep(3)
            try:
                #save documents
                doc_body = WebDriverWait(browser, 15).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'section'))
                )
                image_data = doc_body[1].find_element(By.TAG_NAME, 'wix-image').find_element(By.TAG_NAME, 'img').get_attribute('src')
                doc_url_list = doc_body[1].find_elements(By.TAG_NAME, 'a')
                aux_doc = 0
                while aux_doc < (len(doc_url_list)-1):
                    if doc_text == '':
                        doc_text = f'"{doc_url_list[aux_doc].text.capitalize()}":"{doc_url_list[aux_doc].get_attribute("href")}"'
                    else:
                        doc_text += f',"{doc_url_list[aux_doc].text.capitalize()}":"{doc_url_list[aux_doc].get_attribute("href")}"'
                    aux_doc += 1
                sleep(1)
            except Exception as do:
                print(do)


            try:
                #save data
                sleep(2)
                details_frame = browser.find_element(By.CLASS_NAME, '_49_rs')
                sleep(1)
                browser.switch_to.frame(details_frame)
                sleep(1)
                table_details = browser.find_element(By.ID, 'accordion').find_elements(By.TAG_NAME, 'li')

                count_series = 0
                for data in table_details:
                    aux_count_serie = 0
                    while aux_count_serie < (len(table_details)-1):
                        if 'Série' in table_details[aux_count_serie].text or 'SÉRIE' in table_details[aux_count_serie].text:
                            count_series += 1
                            aux_count_serie += 1
                        else:
                            aux_count_serie += 1
                    if count_series == 1:
                        if 'Série' in data.text or 'SÉRIE' in table_details[aux_count_serie].text:
                            data.find_element(By.TAG_NAME, 'button').click()
                            sleep(1)
                            file_text = table_details[1].text
                            data.find_element(By.TAG_NAME, 'button').click()
                    else:
                        if 'Série' in data.text or 'SÉRIE' in table_details[aux_count_serie].text:
                            data.find_element(By.TAG_NAME, 'button').click()
                            sleep(1)
                            file_text = table_details[1].text
                            data.find_element(By.TAG_NAME, 'button').click()
                    count_series = 0
                filename = image_data + f'- Posição: {aux_data+1}'
                filepath = Path(pc.CRA_PATH) / f"s-{utils.hashed(filename)}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filepath.exists():
                    if filename == '':
                        browser.get(pc.CRA_URL)
                        sleep(5)
                        scroll(browser)
                        sleep(2)
                        table_data = browser.find_elements(By.CLASS_NAME, 'item-link-wrapper')
                        sleep(1)
                        continue
                    else:
                        browser.get(pc.CRA_URL)
                        sleep(5)
                        scroll(browser)
                        sleep(2)
                        table_data = browser.find_elements(By.CLASS_NAME, 'item-link-wrapper')
                        sleep(1)
                        aux_data += 1
                        print(f'já existe {filename}')
                        continue
                else:

                    payload_emissor = {}
                    for data in table_details:
                        aux_details = 0
                        title = data.find_element(By.TAG_NAME, 'h3').text.capitalize()
                        data.find_element(By.TAG_NAME, 'button').click()
                        sleep(2)
                        details_text = data.find_elements(By.TAG_NAME, 'span')
                        while aux_details < len(details_text):
                            detail_splited = details_text[aux_details].text.split(':')
                            if details_payload_text == '':
                                details_payload_text = f'"{detail_splited[0]}":"{detail_splited[1]}"'
                            else:
                                details_payload_text += f',"{detail_splited[0]}":"{detail_splited[1]}"'
                            aux_details += 2
                        sleep(1)
                        details_payload_text = "{" + details_payload_text + "}"
                        details_json = json.loads(details_payload_text)
                        payload_emissor[title] = details_json
                        details_payload_text = ''
                        sleep(1)
                        data.find_element(By.TAG_NAME, 'button').click()
            except Exception as da:
                print('')
                payload_emissor = {}
            sleep(1)
            if filename == '' and image_data != '':
                filename = image_data + f'- Posição: {aux_data + 1}'
            if doc_text == {} and payload_text == {} or filename == '':
                browser.get(pc.CRA_URL)
                sleep(5)
                scroll(browser)
                sleep(2)
                table_data = browser.find_elements(By.CLASS_NAME, 'item-link-wrapper')
                sleep(1)
                continue
            payload_text["Emissor"] = payload_emissor
            doc_text = "{" + doc_text + "}"
            doc_json = json.loads(doc_text)
            payload_text["Documentos"] = doc_json
            sleep(1)
            print(f"salvar")
            Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as fp:
                dump(payload_text, fp, ensure_ascii=False, indent=1)
            aux_data += 1
            browser.get(pc.CRA_URL)
            sleep(5)
            scroll(browser)
            sleep(2)
            table_data = browser.find_elements(By.CLASS_NAME, 'item-link-wrapper')
            sleep(1)
            scroll_value = 200
            aux_validator = 0
        except Exception as h:
            print(h)


def scroll(browser):
    scroll_value = 200
    while scroll_value < 1000:
        try:
            last_scroll_value = scroll_value
            scroll_value += 200
            browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
            sleep(1)
        except Exception as scro:
            print(scro)
    browser.execute_script(f"window.scrollTo(1000, -500)")