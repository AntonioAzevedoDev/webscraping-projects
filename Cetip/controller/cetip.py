from datetime import datetime
from json import dump, load
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Cetip.data import pathandcredentials as pc
from Cetip.utils import utils


def get_data(browser, overwrite=False, type_file = 'estoque'):
    try:
        # explore(browser)
        ativos = utils.get_opcoes(browser)
        ativos = utils.clean_list(ativos)
        header_text = []
        payload = []
        for ativo in ativos:
            try:

                filepath = Path(pc.ACT_PATH) / ativo / type_file
                filename = filepath / f"{type_file}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filename.exists():
                    continue
                else:
                    browser.get(pc.BASE_URL.format(pc.ATIVOS_URL[f'{type_file}'].format(ativo)))
                    sleep(3)
                    utils.set_date_range(browser)
                    if len(browser.find_elements(By.ID, 'header')) > 0:
                        if 'Error' in browser.find_element(By.ID, 'header').text:
                            continue
                    browser.find_element(
                        By.CSS_SELECTOR,
                        'a.button:nth-child(2)'
                    ).click()
                    sleep(3)
                    url = browser.find_element(By.CSS_SELECTOR, '.primary-text > a:nth-child(1)').get_attribute('href')

                    header_text = browser.find_element(By.CSS_SELECTOR,'div.row:nth-child(4) > div:nth-child(1)').find_element(By.TAG_NAME,'label').text.replace('Observações:', '').split('\n')
                    payload.append({
                        'Observações': header_text
                    })
                    try:
                        while browser.find_element(By.CSS_SELECTOR, '.btProxAnt').is_displayed():

                            try:
                                header_text.remove('')
                                header_text.remove(" ")
                            except Exception as e:
                                print()
                            header = []
                            header_precos = []
                            body = browser.find_element(By.CSS_SELECTOR, '.responsive > tbody:nth-child(2)')
                            if type_file != 'volume':
                                try:
                                    header = [
                                        col.text
                                        for col in browser.find_element(
                                            By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(1)"
                                        ).find_elements(By.TAG_NAME, "td")
                                    ]
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    header = [
                                        col.text
                                        for col in browser.find_element(
                                            By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(1)"
                                        ).find_elements(By.TAG_NAME, "td")
                                    ]
                                    header = utils.check_second_header(browser, header)
                                except Exception as e:
                                    print(e)

                            if type_file == 'negocios':

                                header_precos = [
                                    col.text
                                    for col in browser.find_element(
                                        By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(2)"
                                    ).find_elements(By.TAG_NAME, "td")
                                ]

                            for row in body.find_elements(By.TAG_NAME, 'tr'):
                                try:
                                    row_details = [
                                        col.text
                                        for col in row.find_elements(By.TAG_NAME, 'td')
                                    ]
                                except Exception as e:
                                    print(e)
                                if utils.check_string(row.text):
                                    #header = row.text.split(' ')
                                    print('')
                                else:
                                    active_text = row_details
                                    if active_text[0] == '' or active_text[0] == ' ' or active_text[0] == '     Próximo' or active_text[0] == 'Anterior    |    Próximo':
                                        continue
                                    else:
                                        active_text_clean = []
                                        for active in active_text:
                                            if not active == '':
                                                active_text_clean.append(active)
                                        active_text = active_text_clean
                                        if len(header) == 2:
                                            payload.append(
                                                {
                                                    header[0]: active_text[0],
                                                    header[1]: active_text[1]
                                                }
                                            )
                                        else:
                                            try:
                                                if header_precos == []:

                                                    aux_header = 1
                                                    payload_info = [f'{header[0].strip()}: {active_text[0].strip()}']
                                                    payload_products = []
                                                    aux_list = 0
                                                    while aux_header < len(header):
                                                        payload_info[0] = payload_info[0] + f'\n{header[aux_header].strip()}: {active_text[aux_header].strip()}'
                                                        aux_header += 1
                                                    list_info = payload_info[0].split('\n')

                                                    for info in list_info:
                                                        if ':' in info:
                                                            list_product = info.split(':')
                                                            try:
                                                                payload_products[0].update({list_product[0].strip(): list_product[1].strip()})
                                                            except Exception as e:
                                                                payload_products.append({list_product[0].strip(): list_product[1].strip()})
                                                            aux_list += 1
                                                    payload.append(payload_products)
                                                else:
                                                    aux_header = 1
                                                    payload_info = [f'{header[0].strip()}: {active_text[0].strip()}']
                                                    payload_products = []
                                                    aux_list = 0
                                                    while aux_header < len(header):
                                                        payload_info[0] = payload_info[
                                                                              0] + f'\n{header[aux_header].strip()}: {active_text[aux_header].strip()}'
                                                        aux_header += 1
                                                    list_info = payload_info[0].split('\n')

                                                    for info in list_info:
                                                        list_product = info.split(':')
                                                        try:
                                                            if list_product[0] == 'Preços':
                                                                payload_products[0].update({
                                                                    'Preço': {
                                                                        'Mínimo': active_text[5],
                                                                        'Médio': active_text[6],
                                                                        'Máximo': active_text[7]
                                                                    }
                                                                })
                                                            elif list_product[0] == 'Valor Financeiro':
                                                                payload_products[0].update({
                                                                    'Valor Financeiro': active_text[8]
                                                                })
                                                            else:
                                                                payload_products[0].update({list_product[0].strip(): list_product[1].strip()})
                                                        except Exception as e:
                                                            payload_products.append({list_product[0].strip(): list_product[1].strip()})
                                                        aux_list += 1
                                                    payload.append(payload_products)
                                            except Exception as e:
                                                print(e)

                            btn_pagination = browser.find_element(By.CSS_SELECTOR, '.Cabecalho_02').find_elements(
                                By.TAG_NAME, 'a')
                            validator = False
                            for btn in btn_pagination:
                                if 'Próximo' in btn.text:
                                    btn.click()
                                    validator = True
                            if validator == False:
                                break
                            sleep(2)
                            try:
                                next_button = browser.find_element(By.CSS_SELECTOR, 'a.btProxAnt:nth-child(2)')
                            except Exception as e:
                                print('')
                    except Exception as e:
                        try:
                            btn_ant = browser.find_element(By.CSS_SELECTOR, 'a.btProxAnt:nth-child(1)').is_displayed()
                        except Exception as e:
                            try:
                                header_text.remove('')
                                header_text.remove(" ")
                            except Exception as e:
                                print()
                            header = []
                            body = browser.find_element(By.CSS_SELECTOR, '.responsive > tbody:nth-child(2)')
                            header = [
                                col.text
                                for col in browser.find_element(
                                    By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(1)"
                                ).find_elements(By.TAG_NAME, "td")
                            ]
                            for row in body.find_elements(By.TAG_NAME, 'tr'):

                                if utils.check_string(row.text):
                                    # header = row.text.split(' ')
                                    print('')
                                else:
                                    active_text = row.text.split(' ')
                                    if active_text[0] == '' or active_text[0] == ' ':
                                        continue
                                    else:
                                        active_text_clean = []
                                        for active in active_text:
                                            if not active == '':
                                                active_text_clean.append(active)
                                        active_text = active_text_clean
                                        if len(header) == 2:
                                            payload.append(
                                                {
                                                    header[0]: active_text[0].strip(),
                                                    header[1]: active_text[1].strip()
                                                }
                                            )
                                        else:

                                            aux_header = 1
                                            payload_info = [f'{header[0].strip()}: {active_text[0].strip()}']
                                            payload_products = []
                                            aux_list = 0
                                            while aux_header < len(header):
                                                payload_info[0] = payload_info[
                                                                      0] + f'\n{header[aux_header]}: {active_text[aux_header]}'
                                                aux_header += 1
                                            list_info = payload_info[0].split('\n')

                                            for info in list_info:
                                                list_product = info.split(':')
                                                try:
                                                    if list_product[0] == 'Preços':
                                                        payload_products[0].update({
                                                            'Preço': {
                                                                    'Mínimo': active_text[5].strip(),
                                                                    'Médio': active_text[6].strip(),
                                                                    'Máximo': active_text[7].strip()
                                                            }
                                                        })
                                                    elif list_product[0] == 'Valor Financeiro':
                                                        payload_products[0].update({
                                                            'Valor Financeiro': active_text[8].strip()
                                                        })
                                                    else:
                                                        payload_products[0].update({list_product[0].strip(): list_product[1].strip()})
                                                except Exception as e:
                                                    payload_products.append({list_product[0].strip(): list_product[1].strip()})
                                                aux_list += 1
                                            payload.append(payload_products)
                        print(e)
                        print('Lista Finalizada')
                    filepath.mkdir(parents=True, exist_ok=True)
                    with open(filename, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                        payload = []
                        print('next active')
            except Exception as e:
                continue
    except Exception as e:
        print(e)


def save_volume_information(browser, overwrite=False, type_file='volume'):
    try:
        # explore(browser)
        ativos = utils.get_opcoes(browser)
        print(len(ativos), ativos)
        ativos = utils.clean_list(ativos)
        header_text = []

        for ativo in ativos:
            payload = []
            try:

                filepath = Path(pc.ACT_PATH) / ativo / type_file
                filename = filepath / f"{type_file}-{datetime.now().strftime('%Y%m%d')}.json"
                if not overwrite and filename.exists():
                    continue
                else:
                    try:
                        print(pc.BASE_URL.format(pc.ATIVOS_URL[f'{type_file}'].format(ativo)))
                        browser.get(pc.BASE_URL.format(pc.ATIVOS_URL[f'{type_file}'].format(ativo)))
                        sleep(3)
                        utils.set_date_range(browser)
                        if len(browser.find_elements(By.ID, 'header')) > 0:
                            if 'Error' in browser.find_element(By.ID, 'header').text:
                                continue
                        browser.find_element(
                            By.CSS_SELECTOR,
                            'a.button:nth-child(2)'
                        ).click()
                        sleep(3)
                        url = browser.find_element(By.CSS_SELECTOR, '.primary-text > a:nth-child(1)').get_attribute('href')
                        header_text = browser.find_element(By.CSS_SELECTOR,'div.row:nth-child(4) > div:nth-child(1)').find_element(By.TAG_NAME,'label').text.replace('Observações:', '').split('\n')
                        payload.append({
                            'Observações': header_text
                        })
                        try:
                            while browser.find_element(By.CSS_SELECTOR, '.btProxAnt').is_displayed():

                                try:
                                    header_text.remove('')
                                    header_text.remove(" ")
                                except Exception as e:
                                    print()
                                header = []
                                header_precos = []
                                body = browser.find_element(By.CSS_SELECTOR, '.responsive > tbody:nth-child(2)')
                                if type_file != 'volume':
                                    header = [
                                        col.text
                                        for col in browser.find_element(
                                            By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(1)"
                                        ).find_elements(By.TAG_NAME, "td")
                                    ]
                                else:
                                    try:
                                        header = [
                                            col.text
                                            for col in browser.find_element(
                                                By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(1)"
                                            ).find_elements(By.TAG_NAME, "td")
                                        ]
                                        header_aux = utils.check_second_header(browser, header)
                                    except Exception as e:
                                        print(e)

                                if type_file == 'negocios':

                                    header_precos = [
                                        col.text
                                        for col in browser.find_element(
                                            By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(2)"
                                        ).find_elements(By.TAG_NAME, "td")
                                    ]

                                for row in body.find_elements(By.TAG_NAME, 'tr'):
                                    try:
                                        row_details = [
                                            col.text
                                            for col in row.find_elements(By.TAG_NAME, 'td')
                                        ]
                                    except Exception as e:
                                        print(e)
                                    if utils.check_string(row.text):
                                        #header = row.text.split(' ')
                                        print('')
                                    else:
                                        active_text = row_details
                                        if header_aux == []:
                                            header_aux = utils.check_second_header(browser, header)
                                        if active_text[0] == '' or active_text[0] == ' ' or active_text[0] == '     Próximo' or active_text[0] == 'Anterior    |    Próximo':
                                            continue
                                        else:

                                            if len(header) == 2:
                                                payload.append(
                                                    {
                                                        header[0]: active_text[0].strip(),
                                                        header[1]: active_text[1].strip()
                                                    }
                                                )
                                            else:
                                                if header_precos == []:
                                                    if len(header) == len(active_text):

                                                        aux_header = 1
                                                        payload_info = [f'{header[0].strip()}: {active_text[0].strip()}']
                                                        payload_products = []
                                                        aux_list = 0
                                                        while aux_header < len(header):
                                                            payload_info[0] = payload_info[0] + f'\n{header[aux_header].strip()}: {active_text[aux_header].strip()}'
                                                            aux_header += 1
                                                        list_info = payload_info[0].split('\n')

                                                        for info in list_info:
                                                            if ':' in info:
                                                                list_product = info.split(':')
                                                                try:
                                                                    payload_products[0].update({list_product[0].strip(): list_product[1].strip()})
                                                                except Exception as e:
                                                                    payload_products.append({list_product[0].strip(): list_product[1].strip()})
                                                                    continue
                                                                aux_list += 1
                                                        payload.append(payload_products)
                                                    else:
                                                        payload_products = utils.organize_header(header, header_aux, active_text)
                                                        payload.append(payload_products)
                                                else:
                                                    aux_header = 1
                                                    payload_info = [f'{header[0].strip()}: {active_text[0].strip()}']
                                                    payload_products = []
                                                    aux_list = 0
                                                    while aux_header < len(header):
                                                        payload_info[0] = payload_info[
                                                                              0] + f'\n{header[aux_header].strip()}: {active_text[aux_header].strip()}'
                                                        aux_header += 1
                                                    list_info = payload_info[0].split('\n')

                                                    for info in list_info:
                                                        list_product = info.split(':')
                                                        try:
                                                            if list_product[0] == 'Preços':
                                                                payload_products[0].update({
                                                                    'Preço': {
                                                                        'Mínimo': active_text[5].strip(),
                                                                        'Médio': active_text[6].strip(),
                                                                        'Máximo': active_text[7].strip()
                                                                    }
                                                                })
                                                            elif list_product[0] == 'Valor Financeiro':
                                                                payload_products[0].update({
                                                                    'Valor Financeiro': active_text[8].strip()
                                                                })
                                                            else:
                                                                payload_products[0].update({list_product[0].strip(): list_product[1].strip()})
                                                        except Exception as e:
                                                            payload_products.append({list_product[0].strip(): list_product[1].strip()})
                                                        aux_list += 1
                                                    payload.append(payload_products)

                                btn_pagination = browser.find_element(By.CSS_SELECTOR, '.Cabecalho_02').find_elements(By.TAG_NAME, 'a')
                                validator = False
                                for btn in btn_pagination:
                                    if 'Próximo' in btn.text:
                                        btn.click()
                                        validator = True
                                if validator == False:
                                    break
                                sleep(2)
                                try:
                                    next_button = browser.find_element(By.CSS_SELECTOR, 'a.btProxAnt:nth-child(2)')
                                except Exception as e:
                                    print('')
                        except Exception as e:
                            try:
                                btn_ant = browser.find_element(By.CSS_SELECTOR, 'a.btProxAnt:nth-child(1)').is_displayed()
                            except Exception as e:
                                try:
                                    header_text.remove('')
                                    header_text.remove(" ")
                                except Exception as e:
                                    print()
                                header = []
                                body = browser.find_element(By.CSS_SELECTOR, '.responsive > tbody:nth-child(2)')
                                header = [
                                    col.text
                                    for col in browser.find_element(
                                        By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(1)"
                                    ).find_elements(By.TAG_NAME, "td")
                                ]
                                header_aux = utils.check_second_header(browser, header)
                                for row in body.find_elements(By.TAG_NAME, 'tr'):

                                    if utils.check_string(row.text):
                                        # header = row.text.split(' ')
                                        print('')
                                    else:
                                        active_text = row.text.split(' ')
                                        if active_text[0] == '' or active_text[0] == ' ':
                                            continue
                                        else:
                                            active_text_clean = []
                                            for active in active_text:
                                                if not active == '':
                                                    active_text_clean.append(active)
                                            active_text = active_text_clean
                                            if len(header) == 2:
                                                payload.append(
                                                    {
                                                        header[0]: active_text[0].strip(),
                                                        header[1]: active_text[1].strip()
                                                    }
                                                )
                                            else:

                                                aux_header = 1
                                                payload_info = [f'{header[0]}: {active_text[0]}']
                                                payload_products = []
                                                aux_list = 0
                                                while aux_header < len(header):
                                                    payload_info[0] = payload_info[
                                                                          0] + f'\n{header[aux_header].strip()}: {active_text[aux_header].strip()}'
                                                    aux_header += 1
                                                list_info = payload_info[0].split('\n')

                                                for info in list_info:
                                                    list_product = info.split(':')
                                                    try:
                                                        if list_product[0] == 'Preços':
                                                            payload_products[0].update({
                                                                'Preço': {
                                                                        'Mínimo': active_text[5].strip(),
                                                                        'Médio': active_text[6].strip(),
                                                                        'Máximo': active_text[7].strip()
                                                                }
                                                            })
                                                        elif list_product[0] == 'Valor Financeiro':
                                                            payload_products[0].update({
                                                                'Valor Financeiro': active_text[8].strip()
                                                            })
                                                        else:
                                                            payload_products[0].update({list_product[0].strip(): list_product[1].strip()})
                                                    except Exception as e:
                                                        payload_products.append({list_product[0].strip(): list_product[1].strip()})
                                                    aux_list += 1
                                                payload.append(payload_products)
                                print(e)
                            print('Lista Finalizada')
                    except Exception as e:
                        continue

                    filepath.mkdir(parents=True, exist_ok=True)
                    with open(filename, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                        payload = []
                        print('next active')
            except Exception as e:
                print(e)
                continue
        print('finalizado')
    except Exception as e:
        print(e)
