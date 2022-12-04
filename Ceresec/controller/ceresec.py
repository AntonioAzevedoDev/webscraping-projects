import re
from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import ast
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains, Keys
from Ceresec.utils import utils
from Ceresec.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Ceresec data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    title = ''
    try:
        table_data = browser.find_element(By.CSS_SELECTOR, '.emissao-list').find_elements(By.TAG_NAME, 'li')
        aux_title = 2
        for data in table_data:
            if data.get_attribute('class') == '':
                continue
            else:
                title = data.find_element(By.CSS_SELECTOR,
                                         f'li.craItem:nth-child({aux_title}) > a:nth-child(1) > div:nth-child(1) > div:nth-child(2) > p:nth-child(1)')
            filepath = Path(
                pc.CRA_PATH) / f"s-{utils.hashed(title.text)}-{datetime.now().strftime('%Y%m%d')}.json"
            if not overwrite and filepath.exists():
                print(f'Já existe: {title.text}')
                sleep(2)
                aux_title += 1
                continue

            else:
                cra_name = title.text
                text_data = ''
                doc_text = ''
                if data.get_attribute('class') == '':
                    continue
                else:
                    ActionChains(browser).context_click(data).key_down(Keys.CONTROL).click(data).key_up(
                        Keys.CONTROL).perform()
                    sleep(3)
                    browser.switch_to.window(browser.window_handles[1])
                    sleep(2)
                    utils.accept_cookies(browser)
                    series_options = Select(browser.find_element(By.CSS_SELECTOR, '.series'))
                    total_options = len(series_options.options)
                    aux_series = 1

                    while aux_series < total_options:
                        text_fdata = ''
                        serie_text_data = ''
                        features_data = browser.find_element(By.CSS_SELECTOR, '.caracteristicas > div:nth-child(3)').find_elements(By.CLASS_NAME, 'item')
                        for fdata in features_data:
                            fdata_splited = fdata.text.split('\n')
                            if len(fdata_splited) == 1:
                                if text_fdata == '':
                                    text_fdata = f'"{fdata_splited[0].replace(":", "")}":"-"'
                                else:
                                    text_fdata += f'"{fdata_splited[0].replace(":", "")}":"-"'
                            else:
                                for tf in fdata_splited:
                                    if text_fdata == '':
                                        text_fdata = f'"{tf.replace(":","")}"'
                                    else:
                                        text_fdata += f':"{tf}"'
                                    sleep(1)
                            if serie_text_data == '':
                                serie_text_data = text_fdata
                            else:
                                serie_text_data += "," + text_fdata
                            text_fdata = ''
                            sleep(1)
                        if text_data == '':
                            text_data = f'"Serie {aux_series}":' + "{" + serie_text_data + "}"
                        else:
                            text_data += "," + f'"Serie {aux_series}":' + "{" + serie_text_data + "}"
                        serie_text_data = ''
                        aux_series += 1
                        browser.find_element(By.CSS_SELECTOR, '.series').click()
                        try:
                            pattern = re.compile(f'{aux_series}')
                            for option in series_options.options:
                                value = option.get_attribute('text')
                                if pattern.search(value):
                                    option.click()
                                    sleep(2)
                                    series_options = Select(browser.find_element(By.CSS_SELECTOR, '.series'))
                                    break
                        except Exception as se:
                            break

                    #get documents
                    doc_body = browser.find_element(By.CSS_SELECTOR, '#list-areas').find_elements(By.TAG_NAME, 'li')
                    aux_doc = 1
                    doc_text_data = ''
                    for doc in doc_body:
                        doc_name = doc.text

                        if doc.text == '':
                            aux_doc += 1
                            continue
                        else:
                            doc.click()
                            sleep(1)
                            try:
                                avaliable_docs_body = browser.find_element(By.CSS_SELECTOR,
                                                                           f'div.box:nth-child({aux_doc}) > ul:nth-child(2)')
                            except Exception as avd:
                                avaliable_docs_body = browser.find_element(By.CSS_SELECTOR, 'div.row:nth-child(3)').find_element(By.CSS_SELECTOR, 'div.box:nth-child(5)').find_element(By.TAG_NAME, 'ul')
                            avaliable_doc_text = ''
                            avaliable_docs = avaliable_docs_body.find_elements(By.TAG_NAME, 'li')
                            for docs in avaliable_docs:
                                url = docs.find_element(By.TAG_NAME, 'a').get_attribute('href')
                                name = docs.text
                                if avaliable_doc_text == '':
                                    avaliable_doc_text = f'"{name}":"{url}"'
                                else:
                                    avaliable_doc_text += f',"{name}":"{url}"'
                                sleep(1)
                            if doc_text_data == '':
                                doc_text_data = f'"{doc_name}":' + "{" + avaliable_doc_text + "}"
                            else:
                                doc_text_data += f',"{doc_name}":' + "{" + avaliable_doc_text + "}"
                            aux_doc += 1
                            sleep(1)
                        doc_text = ',"Documentos":{' + doc_text_data + "}"



                    text_data = f'"CRA {cra_name}":' + "{" + text_data + doc_text + "}"
                    text_data = "{" + text_data + "}"

                    text_json = json.loads(text_data)
                    payload = text_json
                    print(f'salvar {cra_name}')
                    Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    sleep(1)
                    text_data = ''
                    browser.close()
                    browser.switch_to.window(browser.window_handles[0])
                    sleep(2)
                    aux_title += 1
    except Exception as app:
        print(app)