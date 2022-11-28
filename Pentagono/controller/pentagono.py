from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Pentagono.utils import utils
from Pentagono.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Pentagono data")
    browser.get(pc.CRA_URL)
    sleep(5)
    aux = 0
    utils.close_banner(browser)
    sleep(1)
    browser.find_element(By.CSS_SELECTOR, '#Emissoes > div:nth-child(1) > div:nth-child(1) > div:nth-child(4) > button:nth-child(1)').click()
    body = WebDriverWait(browser, 999).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.table'))
    )
    while True:
        try:
            body_data = body.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME,'tr')
            sleep(3)
            min = 0
            max = 100
            range_data = []
            while max < len(body_data):
                range_data = body_data[min:max]
                aux_range_data = 0
                while aux_range_data < len(range_data):
                    active = range_data[aux_range_data].find_element(By.TAG_NAME,'a')
                    filepath = Path(
                        pc.CRA_PATH) / f"s-{utils.hashed(active.text)}-{datetime.now().strftime('%Y%m%d')}.json"
                    if not overwrite and filepath.exists():
                        print(f'Já existe: {active.text}')
                        sleep(2)
                        aux_range_data += 1
                        continue

                    else:
                        ActionChains(browser).context_click(active).key_down(Keys.CONTROL).click(active).key_up(
                            Keys.CONTROL).perform()
                        sleep(3)
                        browser.switch_to.window(browser.window_handles[1])
                        sleep(2)
                        save_active(browser, filepath)
                        aux_range_data += 1
                        #Close tab
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        sleep(3)
                min += 100
                max += 100
            break
        except Exception as e:
            continue


def save_active(browser, filepath):
    try:
        payload = []
        sleep(2)
        active_name = browser.find_element(By.CSS_SELECTOR,'#tab-1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)').text
        sleep(1)
        active_body = browser.find_element(By.CSS_SELECTOR,'div.row:nth-child(4) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2)').find_elements(By.TAG_NAME, 'tr')
        aux_data = 0
        text_payload = ''

        for data in active_body:
            sleep(1)
            text_data = data.find_elements(By.TAG_NAME,'td')
            sleep(1)
            while aux_data < len(text_data):
                if text_data[aux_data].text == 'Quantidade Prevista *:' or text_data[aux_data].text == 'Valor Nominal na Emissão:' or text_data[aux_data].text == 'Repactuação:' or text_data[aux_data].text == 'Participação nos Lucros:' or text_data[aux_data].text == 'Resgate Antecipado:':
                    aux_data += 2
                elif text_data[aux_data + 1] == '' or len(text_data) < 4:
                    if text_payload == '':
                        text_payload = f'"{text_data[aux_data].text.replace(":","").replace("/"," ou ")}": "-"'
                    else:
                        text_payload += f',"{text_data[aux_data].text.replace(":","").replace("/"," ou ")}": "-"'
                    aux_data += 2
                else:
                    if text_payload == '':
                        text_payload = f'"{text_data[aux_data].text.replace(":","").replace("/"," ou ")}": "{text_data[aux_data + 1].text}"'
                    else:
                        text_payload += f',"{text_data[aux_data].text.replace(":","").replace("/"," ou ")}": "{text_data[aux_data + 1].text}"'
                    aux_data += 2
                sleep(1)
            aux_data = 0
            sleep(1)
        text_payload = "{" + f'"Name:":"{active_name}",' + text_payload + "}"
        payload = json.loads(text_payload)
        print(f"salvar {active_name}")
        Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as fp:
            dump(payload, fp, ensure_ascii=False, indent=1)
    except Exception as active:
        print(active)