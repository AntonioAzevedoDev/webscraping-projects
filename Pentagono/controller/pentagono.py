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
    #test_wire()
    browser.get(pc.CRA_URL)
    sleep(5)
    aux = 0
    utils.close_banner(browser)
    sleep(1)
    browser.find_element(By.CSS_SELECTOR, '#Emissoes > div:nth-child(1) > div:nth-child(1) > div:nth-child(4) > button:nth-child(1)').click()
    body = WebDriverWait(browser, 999).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.table'))
    )
    scroll_value = 100
    last_scroll_value = 200
    aux_range_data = 0
    while True:
        try:
            body_data = body.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME,'tr')
            sleep(3)
            min = 0
            max = 100
            range_data = []
            while max < len(body_data):
                range_data = body_data[min:max]

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
                        ratings = get_ratings(browser)
                        documents = get_documents(browser)
                        save_active(browser, filepath, documents, ratings)
                        aux_range_data += 1
                        #Close tab
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        sleep(3)
                min += 100
                max += 100

        except Exception as e:
            last_scroll_value = scroll_value
            scroll_value += 100
            browser.execute_script(f"window.scrollTo({last_scroll_value}, {scroll_value})")
            continue
        break


def save_active(browser, filepath, documents, ratings):
    try:
        payload = []
        sleep(2)
        active_name = browser.find_element(By.CSS_SELECTOR,'#tab-1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)').text
        sleep(1)
        active_header = browser.find_element(By.CSS_SELECTOR,'#tab-1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2)').find_elements(By.TAG_NAME, 'tr')
        emissor_text = ''
        caract_text = ''
        for head in active_header:
            aux_header = 0
            sleep(1)
            text_data = head.find_elements(By.TAG_NAME, 'td')
            sleep(1)
            while aux_header < (len(text_data)-1):
                if text_data[aux_header].text == '' and 'Escriturador' not in text_data[aux_header].text and 'Coordenador Líder' not in text_data[aux_header].text:
                    aux_header += 2
                    continue

                else:
                    if emissor_text == '':
                        emissor_text = f'"{text_data[aux_header].text}": "{text_data[aux_header+1].text}"'
                    elif text_data[aux_header+1] == '':
                        emissor_text += f',"{text_data[aux_header].text}": "-"'
                    elif 'Escriturador' not in text_data[aux_header].text and 'Coordenador Líder' not in text_data[aux_header].text:
                        emissor_text += f',"{text_data[aux_header].text}": "{text_data[aux_header + 1].text}"'
                    else:
                        aux_header = 2
                    aux_header = 2
                    if caract_text == '':
                        caract_text = f'"{text_data[aux_header].text}": "{text_data[aux_header+1].text}"'
                    elif text_data[aux_header+1] == '':
                        caract_text += f',"{text_data[aux_header].text}": "-"'
                    else:
                        caract_text += f',"{text_data[aux_header].text}": "{text_data[aux_header + 1].text}"'
                    if 'Escriturador' in text_data[aux_header].text and 'Coordenador Líder' in text_data[aux_header].text:
                        caract_text += f',"{text_data[aux_header].text}": "{text_data[aux_header + 1].text}"'
                    aux_header += 1
            sleep(1)
        active_body = browser.find_element(By.CSS_SELECTOR,'div.row:nth-child(4) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2)').find_elements(By.TAG_NAME, 'tr')
        sleep(2)
        aux_data = 0
        text_payload = ''

        for data in active_body:
            sleep(1)
            text_data = data.find_elements(By.TAG_NAME,'td')
            sleep(1)
            while aux_data < len(text_data):

                if text_data[aux_data + 1] == '' or len(text_data) < 4:
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

        emissor_text = "{" + emissor_text + "}"
        emissor_text = f'"Emissor":{emissor_text}'
        emissor_text = "{" + emissor_text + "}"
        caract_text = "{" + caract_text + "}"
        text_payload = "{" + text_payload + "}"
        emissor_json = json.loads(emissor_text)
        caract_json = json.loads(caract_text)
        text_json = json.loads(text_payload)
        payload = emissor_json
        payload["Características da Emissão"] = caract_json
        payload["Características da Série"] = text_json
        payload["Documentos"] = documents
        payload["Ratings"] = ratings
        print(f"salvar {active_name}")
        Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as fp:
            dump(payload, fp, ensure_ascii=False, indent=1)
    except Exception as active:
        print(active)


def get_documents(browser):
    while True:
        try:
            print("save documents")
            browser.find_element(By.CSS_SELECTOR, '#tab2').click()
            sleep(3)
            doc_body = browser.find_element(By.CSS_SELECTOR, '#tab-2 > div:nth-child(2)')
            sleep(1)
            doc_data_text = doc_body.text.replace("ATAS\n", "").replace("DOCUMENTOS DA EMISSÃO\n", "replace").replace("RELATÓRIOS ANUAIS\n", "replace").strip().replace("     ", "")
            doc_urls = doc_body.find_elements(By.TAG_NAME,"a")
            doc_data_splited = doc_data_text.split("replace")
            if len(doc_data_splited) == 3:
                atas_values = doc_data_splited[0].split('\n')
                emission_values = doc_data_splited[1].split('\n')
                reports_values = doc_data_splited[2].split('\n')
                sleep(1)
                atas_urls = ''
                emission_urls = ''
                reports_urls = ''
                aux = 0
                for av in atas_values:
                    if av in doc_urls[aux].text and av != '    ':
                        if atas_urls != '':
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")", "")
                            url = pc.URL_FILE.format(doc_id)
                            atas_urls += f',"{av}": "{url}"'
                            aux += 1
                        else:
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")", "")
                            url = pc.URL_FILE.format(doc_id)
                            atas_urls = f'"{av}": "{url}"'
                            aux += 1
                for ev in emission_values:
                    if ev in doc_urls[aux].text and ev != '    ':
                        if emission_urls != '':
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")", "")
                            url = pc.URL_FILE.format(doc_id)
                            emission_urls += f',"{ev}": "{url}"'
                            aux += 1
                        else:
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(","").replace(")","")
                            url = pc.URL_FILE.format(doc_id)
                            emission_urls = f'"{ev}": "{url}"'
                            aux += 1
                for rv in reports_values:
                    if rv in doc_urls[aux].text and rv != '    ':
                        if reports_urls != '':
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")", "")
                            url = pc.URL_FILE.format(doc_id)
                            reports_urls += f',"{rv}": "{url}"'
                            aux += 1
                        else:
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")", "")
                            url = pc.URL_FILE.format(doc_id)
                            reports_urls = f'"{rv}": "{url}"'
                            aux += 1
            elif len(doc_data_splited) == 2:
                atas_values = doc_data_splited[0].split('\n')
                emission_values = doc_data_splited[1].split('\n')
                sleep(1)
                atas_urls = ''
                emission_urls = ''
                reports_urls = ''
                aux = 0
                for av in atas_values:
                    if av in doc_urls[aux].text and av != '    ':
                        if atas_urls != '':
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")",
                                                                                                                    "")
                            url = pc.URL_FILE.format(doc_id)
                            atas_urls += f',"{av}": "{url}"'
                            aux += 1
                        else:
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")",
                                                                                                                    "")
                            url = pc.URL_FILE.format(doc_id)
                            atas_urls = f'"{av}": "{url}"'
                            aux += 1
                for ev in emission_values:
                    if ev in doc_urls[aux].text and ev != '    ':
                        if emission_urls != '':
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")",
                                                                                                                    "")
                            url = pc.URL_FILE.format(doc_id)
                            emission_urls += f',"{ev}": "{url}"'
                            aux += 1
                        else:
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")",
                                                                                                                    "")
                            url = pc.URL_FILE.format(doc_id)
                            emission_urls = f'"{ev}": "{url}"'
                            aux += 1
            elif len(doc_data_splited) == 1 and 'TEMPORARIAMENTE INDISPONÍVEIS.' not in doc_data_splited[0]:
                atas_values = doc_data_splited[0].split('\n')
                sleep(1)
                atas_urls = ''
                emission_urls = ''
                reports_urls = ''
                aux = 0
                for av in atas_values:
                    if av in doc_urls[aux].text and av != '    ':
                        if atas_urls != '':
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")",
                                                                                                                    "")
                            url = pc.URL_FILE.format(doc_id)
                            atas_urls += f',"{av}": "{url}"'
                            aux += 1
                        else:
                            doc_id = doc_urls[aux].get_attribute("onclick").replace("DownloadBinario(", "").replace(")",
                                                                                                                    "")
                            url = pc.URL_FILE.format(doc_id)
                            atas_urls = f'"{av}": "{url}"'
                            aux += 1
            else:
                pattern_data = '{"Atas":"-","Documentos da Emissão":"-","Relatórios Anuais":"-"}'
                pattern_json = json.loads(pattern_data)
                payload_documents = []
                payload_documents = pattern_json
                browser.find_element(By.CSS_SELECTOR, '#tab1').click()
                sleep(3)
                return payload_documents
            sleep(1)
            atas_urls = "{" + atas_urls + "}"
            atas_urls = "{" + f'"Atas":{atas_urls}' + "}"
            emission_urls = "{" + emission_urls + "}"
            reports_urls = "{" + reports_urls + "}"
            atas_json = json.loads(atas_urls)
            emission_json = json.loads(emission_urls)
            reports_json = json.loads(reports_urls)
            payload_documents = atas_json
            payload_documents["Documentos da Emissão"] = emission_json
            payload_documents["Relatórios Anuais"] = reports_json
            browser.find_element(By.CSS_SELECTOR, '#tab1').click()
            sleep(3)
            return payload_documents
        except Exception as e:
            continue


def get_ratings(browser):
    print('save ratings')
    browser.find_element(By.CSS_SELECTOR, '#tab6').click()
    sleep(3)
    payload = [{'Ratings': '-'}]
    body_ratings = browser.find_element(By.CSS_SELECTOR, '.table-condensed > tbody:nth-child(2)')
    header = browser.find_element(By.CSS_SELECTOR, 'thead.bg-primary').find_elements(By.TAG_NAME, 'th')
    assert len(header) == 4, f"expected 4 cols, got {len(header)}"
    if body_ratings.text != '':
        sleep(1)
    else:
        payload = [{"Ratings":
            {
            header[0].text: '-',
            header[1].text: '-',
            header[2].text: '-',
            header[3].text: '-'
            }
        }]
        return payload


def test_wire():
    from seleniumwire import webdriver

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Go to the Google home page
    driver.get("https://www.pentagonotrustee.com.br/Site/DetalhesEmissor?ativo=10B0002537&aba=tab-2&tipo=3")
    sleep(3)
    driver.find_element(By.CSS_SELECTOR, 'article.bg-light:nth-child(3) > a:nth-child(1)').click()
    sleep(4)
    # Access and print requests via the `requests` attribute
    #for request in driver.requests:
     #   if "DownloadBinario?id=" in request.url:

