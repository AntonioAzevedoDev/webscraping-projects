import json
from datetime import datetime
from json import dump, load
from pathlib import Path
from time import sleep
from Virgo.utils import utils
from Virgo.data import pathandcredentials as pc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def do_login(browser):
    try:
        print('login')
        browser.get(pc.LOGIN_URL)
        sleep(4)
        browser.find_element(By.CSS_SELECTOR, '#email').send_keys(pc.LOGIN_USR)
        browser.find_element(By.CSS_SELECTOR, '#password').send_keys(pc.LOGIN_PWD)
        browser.find_element(By.CSS_SELECTOR, '#next').click()
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.jss26 > div:nth-child(1) > h6:nth-child(1)')))
        browser.get(pc.CRA_URL)
        sleep(3)
    except Exception as lo:
        print(lo)


def save_actions(browser, overwrite=False):
    file_saved = 0
    while True:
        try:
            utils.accept_cookies(browser)
            list_cra = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.gridStyle__GridContainer-sc-19dqjrw-0'))).find_elements(By.TAG_NAME, 'a')
            payload = {}
            aux_cra = 0

            while aux_cra < len(list_cra):
                aux_header = 1
                header_text = ''
                carac_text = ''
                list_cra[aux_cra].click()
                sleep(3)
                body_data = browser.find_element(By.ID, 'emissao-tabpanel-0')
                header_data = body_data.text.split('Outras características')[0]
                header_data = header_data.split('\n')
                title = header_data[0]
                filepath = Path(
                    pc.CRA_PATH) / f"s-{utils.hashed(title)}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filepath.exists():
                    print(f'Já existe: {title}')
                    browser.get(pc.CRA_URL)
                    sleep(3)
                    list_cra = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '.gridStyle__GridContainer-sc-19dqjrw-0'))).find_elements(By.TAG_NAME, 'a')
                    aux_cra += 1
                    file_saved += 1
                    if file_saved == len(list_cra) - 1:
                        break
                    continue
                else:
                    while aux_header < len(header_data):
                        if header_data[aux_header] == 'Em Andamento' or header_data[aux_header] == 'Em Estruturação':
                            break
                        elif header_text == '':
                            header_text = f'"{header_data[aux_header]}":"{header_data[aux_header + 1]}"'
                        else:
                            header_text += f',"{header_data[aux_header]}":"{header_data[aux_header + 1]}"'
                        aux_header += 2

                    sleep(2)
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '.MuiAccordionSummary-content > p:nth-child(2)'))).click()
                    caract_body = browser.find_element(By.CSS_SELECTOR, '.MuiAccordionDetails-root')
                    itens_caract = caract_body.find_elements(By.TAG_NAME, 'p')
                    sleep(1)
                    aux_carac = 0
                    while aux_carac < len(itens_caract):
                        if carac_text == '':
                            carac_text = f'"{itens_caract[aux_carac].text}":"{itens_caract[aux_carac + 1].text}"'
                        else:
                            carac_text += f',"{itens_caract[aux_carac].text}":"{itens_caract[aux_carac + 1].text}"'
                        aux_carac += 2
                    sleep(1)
                    header_text = "{" + header_text + "}"
                    header_json = json.loads(header_text)
                    carac_text = "{" + carac_text + "}"
                    carac_json = json.loads(carac_text)
                    payload["Emissor"] = header_json
                    payload["Características"] = carac_json
                    print(f"salvar")
                    Path(pc.CRA_PATH).mkdir(parents=True, exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    browser.get(pc.CRA_URL)
                    sleep(5)
                    list_cra = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '.gridStyle__GridContainer-sc-19dqjrw-0'))).find_elements(By.TAG_NAME, 'a')
                    aux_cra += 1
                    file_saved += 1
                if file_saved == len(list_cra)-1:
                    break
            break
        except Exception as sa:
            continue
