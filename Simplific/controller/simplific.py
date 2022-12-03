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
from Simplific.utils import utils
from Simplific.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Simplific data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    aux_data = 1
    files_saved = 0
    cra_name_list = []
    while True:
        try:
            list_box = WebDriverWait(browser, 999).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#quemSomosTexto > center:nth-child(5) > form:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1) > span:nth-child(2)'))
            )
            list_box.click()
            list_data = browser.find_element(By.CSS_SELECTOR, '.select2-results').find_elements(By.TAG_NAME, 'li')
            sleep(1)
            if cra_name_list == []:
                cra_name_list = get_name_list(list_data)
            sleep(2)
            while aux_data < len(cra_name_list):
                payload_text = ''
                try:
                    if cra_name_list[aux_data] == list_data[aux_data+1].text:
                        filepath = Path(
                            pc.CRA_PATH) / f"s-{utils.hashed(cra_name_list[aux_data])}-{datetime.now().strftime('%Y%m%d')}.json"
                        if not overwrite and filepath.exists():
                            print(f'Já existe: {(cra_name_list[aux_data])}')
                            sleep(2)
                            aux_data += 1
                            continue
                        else:
                            list_data[aux_data].click()
                            browser.find_element(By.CSS_SELECTOR,'#quemSomosTexto > center:nth-child(5) > form:nth-child(1) > input:nth-child(3)').click()
                            sleep(2)
                            validator = False
                            try:
                                login_text = browser.find_element(By.CSS_SELECTOR, '#conteudoFormularioLogin > center:nth-child(1) > span:nth-child(1)')
                                validator = True
                                browser.get(pc.CRA_URL)
                                sleep(5)
                            except Exception as e:
                                validator = False
                            if validator == True:
                                aux_data += 1
                                files_saved += 1
                                break
                            body = browser.find_element(By.CSS_SELECTOR,'#tabelaCaracteristicas > tbody:nth-child(1)').find_elements(By.TAG_NAME,'tr')
                            for row in body:
                                data = row.find_elements(By.TAG_NAME, 'td')
                                if 'Série' in data[0].text:
                                    continue
                                elif payload_text == '':
                                    payload_text = f'"{data[0].text}": "{data[1].text}"'
                                elif data[1].text == '':
                                    payload_text += f',"{data[0].text}": "-"'
                                else:
                                    payload_text += f',"{data[0].text}": "{data[1].text}"'
                            payload_text = "{" + payload_text + "}"
                            payload = json.loads(payload_text)
                            print(f"salvar")
                            Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                            with open(filepath, "w", encoding="utf-8") as fp:
                                dump(payload, fp, ensure_ascii=False, indent=1)
                            browser.get(pc.CRA_URL)
                            sleep(5)
                            files_saved += 1
                            aux_data += 1
                            break
                    else:
                        aux_data += 1
                        files_saved += 1
                        continue
                except Exception as l:
                    list_box.click()
                    continue
            if aux_data < len(cra_name_list):
                continue
            else:
                break
        except Exception as e:
            print(e)


def get_name_list(list_data):
    aux = 1
    cra_name_list = []
    while aux < len(list_data):
        sleep(1)
        cra_name_list.append(list_data[aux].text)
        aux += 1
    return cra_name_list

