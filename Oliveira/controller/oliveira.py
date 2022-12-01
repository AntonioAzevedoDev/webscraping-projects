from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Oliveira.utils import utils
from Oliveira.data import pathandcredentials as pc


def save_cra(browser, overwrite=False):

    print("Dashboard data")
    browser.get(pc.CRA_URL)
    sleep(5)
    aux = 0
    WebDriverWait(browser, 999).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        'div.title:nth-child(4)'))
    )
    cra_button = WebDriverWait(browser, 999).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.searchbar-filter-type-container:nth-child(4) > div:nth-child(1) > button:nth-child(1)'))
    )
    cra_button.click()
    sleep(2)
    while True:
        actives = browser.find_element(By.CSS_SELECTOR, '.titles-container').find_elements(By.CLASS_NAME, 'title')
        payload = []
        while len(actives) > aux:
            try:
                actives[aux].click()
            except Exception as r:
                break
            sleep(2)
            header_data = WebDriverWait(browser, 999).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '.details-resume-content'))
            )
            name = header_data.find_element(By.CSS_SELECTOR, '.details-name').text
            emissor = browser.find_element(By.CSS_SELECTOR,'div.details-item:nth-child(1) > div:nth-child(2)').text
            codigo = browser.find_element(By.CSS_SELECTOR,'div.details-item:nth-child(3) > div:nth-child(2)').text
            filepath = Path(
                pc.CRA_PATH) / f"s-{utils.hashed(name+'-'+emissor+'-'+codigo)}-{datetime.now().strftime('%Y%m%d')}.json"
            if not overwrite and filepath.exists():
                print(f'Já existe: {name}')
                aux += 1
                browser.find_element(By.CSS_SELECTOR, '.fa-arrow-left').click()
                sleep(1)
                break
            else:
                serie = header_data.find_element(By.CSS_SELECTOR, '.details-title-name').text
                serie_details = serie.split(' ')
                header_data = f'"Nome: ":"{name}"'
                header_data += f',"Serie":"{serie_details[1]}"'
                header_data += f',"Emissao":"{serie_details[2]}"'
                body_series = browser.find_element(By.CSS_SELECTOR, '.details-items').find_elements(By.CLASS_NAME, 'details-item')
                series_data = ''
                emission_data = ''
                for series_item in body_series:
                    data = series_item.text.split('\n')
                    if data[0] == 'Atualização Monetária:' or data[0] == 'Valor Nominal:' or data[0] == 'Quantidade de ativos:':
                        continue
                    else:
                        try:
                            if series_data != '':
                                series_data += f',"{data[0].replace(":","")}":"{data[1]}"'
                            else:
                                series_data += f'"{data[0].replace(":","")}":"{data[1]}"'
                        except Exception as e:
                            series_data += f',"{data[0].replace(":","")}":"-"'
                            continue
                series_data = "{" + series_data + "}"

                browser.find_element(By.CSS_SELECTOR,'button.details-option-button:nth-child(2)').click()
                sleep(2)
                emission_body = browser.find_element(By.CSS_SELECTOR, '.details-items').find_elements(By.CLASS_NAME, 'details-item')
                for emission_item in emission_body:
                    data = emission_item.text.split('\n')
                    if data[0] == 'Número de Séries:' or data[0] == 'Número da Emissão:' or data[0] == 'Volume Total:':
                        if emission_data != '':
                            try:
                                if emission_data != '':
                                    emission_data += f',"{data[0].replace(":","")}":"{data[1]}"'
                                else:
                                    emission_data += f'"{data[0].replace(":","")}":"{data[1]}"'
                            except Exception as e:
                                emission_data += f',"{data[0].replace(":","")}":"-"'
                                continue
                        else:
                            emission_data += f'"{data[0].replace(":","")}":"{data[1]}"'
                    else:
                        continue
                emission_data = "{" + emission_data + "}"
                sleep(2)
                #Find documents
                browser.find_element(By.CSS_SELECTOR,'.fa-chevron-down').click()
                documents = browser.find_element(By.CSS_SELECTOR,'.details-downloads > div:nth-child(1) > div:nth-child(2)').find_elements(By.TAG_NAME,'a')
                documents_text = ''
                for doc in documents:
                    if documents_text != '':
                        documents_text += f',"{doc.get_attribute("text")}":"{doc.get_attribute("href")}"'
                    else:
                        documents_text += f'"{doc.get_attribute("text")}":"{doc.get_attribute("href")}"'
                documents_text = "{" + documents_text + "}"
                #Go back
                browser.find_element(By.CSS_SELECTOR, '.fa-arrow-left').click()
                sleep(2)

                sleep(1)
                json_data = {}
                header_data = "{" + header_data + "}"
                json_header = json.loads(header_data)
                json_serie = json.loads(series_data)
                json_emission = json.loads(emission_data)
                json_documents = json.loads(documents_text)
                payload = json_header
                payload["Descrição da Série"] = json_serie
                payload["Emissão"] = json_emission
                payload["Documentos"] = json_documents
                try:
                    print(f"salvar {name}")
                    Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    payload = []
                    aux += 1

                except Exception as save:
                    print(save)
        if not len(actives) > aux:
            break
        else:
            continue
