from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json
from selenium.webdriver.common.by import By

from Commcor.utils import utils
from Commcor.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):

    print("Dashboard data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)

    while True:
        try:
            browser.find_element(By.CSS_SELECTOR, '#tab2-tab').click()
            browser.find_element(By.CSS_SELECTOR,
                                 'div.dropdown:nth-child(3) > button:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
        except Exception as tab:
            browser.refresh()
            continue
        #Buscar código do ativo!!!!

        sleep(1)
        cra_elements = []
        payload = []
        text_payload = ''
        total_cra = 0
        total_saved = 0
        while cra_elements == [] or len(cra_elements) == 1:
            try:
                cra_elements = browser.find_element(By.CSS_SELECTOR,'#bs-select-3 > ul:nth-child(1)').find_elements(By.TAG_NAME,'li')
                sleep(1)
                if len(cra_elements) == 1:
                    browser.refresh()
                    sleep(3)
                    continue
                else:
                    total_cra = len(cra_elements)
                    sleep(1)

                    # Buscar código do ativo!!!!
                    for cra in cra_elements:
                        if cra.text == 'Selecione um Cód. Ativo':
                            continue

                        try:
                            cra.click()
                        except Exception as cra_click:
                            browser.find_element(By.CSS_SELECTOR,
                                                 'div.dropdown:nth-child(3) > button:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
                            cra.click()
                        sleep(2)
                        title = browser.find_element(By.CSS_SELECTOR,
                                                    '#emissoesAjax > li:nth-child(1) > div:nth-child(5)').text
                        filepath = Path(
                            pc.CRA_PATH) / f"s-{utils.hashed(title)}-{datetime.now().strftime('%Y%m%d')}.json"
                        if not overwrite and filepath.exists():
                            print(f'Já existe: {cra.text}')
                            text_payload = ''
                            payload = []
                            browser.find_element(By.CSS_SELECTOR,
                                                     'div.dropdown:nth-child(3) > button:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
                            continue
                            sleep(2)
                        else:
                            sleep(1)
                            browser.find_element(By.CSS_SELECTOR,'#emissoesAjax').click()
                            column_values = []
                            values = []
                            try:
                                column_values = browser.find_element(By.CSS_SELECTOR,'#panel-emissor-tab1').find_elements(By.TAG_NAME,'b')
                                values = browser.find_element(By.CSS_SELECTOR, '#panel-emissor-tab1').find_elements(By.TAG_NAME,'span')
                                aux = 0

                                while aux < len(column_values):
                                    if values[aux].text == '':
                                        if text_payload != '':
                                            text_payload += f',"{column_values[aux].text}":"-"'
                                            aux += 1
                                        else:
                                            text_payload += f'"{column_values[aux].text}":"-"'
                                            aux += 1
                                    else:
                                        if text_payload != '':
                                            text_payload += f',"{column_values[aux].text}":"{values[aux].text}"'
                                            aux += 1
                                        else:
                                            text_payload += f'"{column_values[aux].text}":"{values[aux].text}"'
                                            aux += 1
                                sleep(1)
                            except Exception as e:
                                print(e)
                            try:
                                text_payload = "{" + text_payload + "}"
                                json_data = {}
                                json_data = json.loads(text_payload)
                                payload = json_data
                                print(f"salvar {title}")
                                Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                                with open(filepath, "w", encoding="utf-8") as fp:
                                    dump(payload, fp, ensure_ascii=False, indent=1)
                                text_payload = ''
                                payload = []
                                total_saved += 1
                            except Exception as js:
                                print(js)


            except Exception as app:
                browser.refresh()
                continue
        if (total_cra-1) != total_saved:
            continue
        break
