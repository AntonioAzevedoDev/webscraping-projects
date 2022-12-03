from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import ast
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Canal_Securitizadora.utils import utils
from Canal_Securitizadora.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):
    print("Canal Securitizadora data")
    browser.get(pc.CRA_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(1)
    text_data = ''
    try:
        while True:
            aux_text = ''
            aux_data = 0
            aux_doc = 1
            canal_data = browser.find_element(By.CSS_SELECTOR, 'div.highlights:nth-child(1)').find_elements(By.TAG_NAME, 'section')
            while aux_doc <= len(canal_data):
                for data in canal_data:
                    title = data.find_element(By.CSS_SELECTOR, f'div.highlights:nth-child(1) > section:nth-child({aux_doc}) > div:nth-child(1) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2)')
                    emission = data.find_element(By.CSS_SELECTOR, f'div.highlights:nth-child(1) > section:nth-child({aux_doc}) > div:nth-child(1) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2)')
                    filepath = Path(
                        pc.CRA_PATH) / f"s-{utils.hashed(title.text+'-'+emission.text)}-{datetime.now().strftime('%Y%m%d')}.json"
                    if not overwrite and filepath.exists():
                        print(f'Já existe: {title.text}')
                        sleep(2)
                        aux_doc += 1
                        continue

                    else:
                        try:
                            body_data = data.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                            for db in body_data:
                                db_data = db.find_elements(By.TAG_NAME, 'td')
                                while aux_data < len(db_data):
                                    if aux_text == '':
                                        name = db_data[aux_data].text.replace("\n", " ")
                                        aux_text = f'"{name}"'
                                        aux_data += 1
                                    else:
                                        aux_text += f':"{db_data[aux_data].text}"'
                                        aux_data += 1
                                if text_data == '':
                                    text_data = aux_text
                                else:
                                    text_data += "," + aux_text
                                aux_text = ''
                                aux_data = 0
                                sleep(1)
                            text_data = "{" + text_data + "}"
                            text_json = json.loads(text_data)
                            payload = text_json
                            print(f'salvar {title.text}')
                            Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                            with open(filepath, "w", encoding="utf-8") as fp:
                                dump(payload, fp, ensure_ascii=False, indent=1)
                            aux_doc += 1
                            sleep(2)
                            text_data = ''
                        except Exception as s:
                            continue
            break
    except Exception as app:
        print(app)