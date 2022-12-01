from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Planner.utils import utils
from Planner.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Planner data")
    browser.get(pc.CRA_URL)
    sleep(5)
    aux = 0
    utils.close_banner_and_accept_cookies(browser)
    sleep(1)
    body = WebDriverWait(browser, 999).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#tablepress-41'))
    )
    while True:
        try:
            body_data = body.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME,'tr')
            sleep(3)
            while aux < len(body_data):
                code = body_data[aux].find_element(By.CLASS_NAME, 'column-4')
                filepath = Path(
                    pc.CRA_PATH) / f"s-{utils.hashed(code.text)}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filepath.exists():
                    print(f'Já existe: {code.text}')
                    sleep(2)
                    aux += 1
                    continue
                else:
                    element = WebDriverWait(body_data[aux], 999).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'a'))
                    )
                    element.click()
                    sleep(2)
                    browser.switch_to.window(browser.window_handles[1])
                    sleep(3)
                    #cra_data = browser.find_element(By.CSS_SELECTOR,'.elementor-inner > div:nth-child(1)').find_elements(By.TAG_NAME,'section')
                    cra_data = WebDriverWait(browser, 999).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.elementor-inner > div:nth-child(1)'))
                    ).find_elements(By.TAG_NAME, 'section')
                    aux_cra = 0
                    payload_text = ''
                    clear_cra_data = cra_data
                    while aux_cra < len(cra_data):
                        if cra_data[aux_cra].text == '':
                            clear_cra_data.remove(cra_data[aux_cra])

                        aux_cra += 1
                    clear_cra_data = clear_cra_data[5:len(clear_cra_data)]
                    sleep(1)
                    try:
                        for data in clear_cra_data:
                            titles = data.find_elements(By.TAG_NAME, 'h3')
                            values = data.find_elements(By.TAG_NAME, 'p')
                            sleep(1)
                            quant_data = 0
                            if len(titles) == len(values):
                                while quant_data < len(titles):
                                    if payload_text == '':
                                        payload_text = f'"{titles[quant_data].text}": "{values[quant_data].text}"'
                                        quant_data += 1
                                    elif values[quant_data] == '':
                                        payload_text += f',"{titles[quant_data].text}": "-"'
                                        quant_data += 1
                                    else:
                                        payload_text += f',"{titles[quant_data].text}": "{values[quant_data].text}"'
                                        quant_data += 1
                    except Exception as d:
                        print('')

                    #get extra documents
                    try:
                        docs_rows = WebDriverWait(browser, 50).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.elementor-element-2d366fb > div:nth-child(1) > div:nth-child(1)'))
                        ).find_elements(By.CLASS_NAME, 'elementor-accordion-item')
                        text_doc = ''
                        text_doc_body = ''
                        doc_payload = []
                        check_values = []
                        aux_check = 0
                        for doc in docs_rows:
                            doc.click()

                            sleep(1)
                            values = doc.find_elements(By.TAG_NAME, 'a')
                            for value in values:
                                validator = False
                                if check_values != [] and doc_payload != []:

                                    while aux_check < len(check_values):
                                        try:
                                            if f'"{check_values[aux_check]}' + '":{' in doc_payload[aux_check]:
                                                validator = True
                                                aux_check += 1
                                                break
                                            else:
                                                aux_check += 1
                                        except Exception as ch:
                                            break
                                if text_doc != '' and validator == False and doc_payload != [] and text_doc_body != '':
                                    if value.get_attribute("href") != '':
                                        text_doc_body += f',"{value.get_attribute("text")}": "{value.get_attribute("href")}"'
                                    else:
                                        text_doc += f',"{value.get_attribute("text")}":' + '{'
                                elif text_doc != '' and validator == False and text_doc_body != '':
                                    text_doc_body += f',"{value.get_attribute("text")}": "{value.get_attribute("href")}"'
                                else:
                                    if value.get_attribute("href") != '':
                                        text_doc_body += f'"{value.get_attribute("text")}": "{value.get_attribute("href")}"'
                                    else:
                                        text_doc += f'"{value.get_attribute("text")}":' + '{'
                                        check_values.append(value.get_attribute("text"))
                            text_doc = text_doc + text_doc_body + '}'
                            doc_payload.append(text_doc)
                            text_doc = ''
                            text_doc_body = ''
                    except Exception as d:
                        print(d)
                    try:
                        for payload_data in doc_payload:
                            payload_text += "," + payload_data
                        payload_text = "{" + payload_text + "}"
                        payload = json.loads(payload_text)

                        print(f"salvar")
                        Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                        with open(filepath, "w", encoding="utf-8") as fp:
                            dump(payload, fp, ensure_ascii=False, indent=1)
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        sleep(3)
                        aux += 1
                    except Exception as s:
                        print(s)
            break
        except Exception as b:
            print(b)

