from datetime import datetime
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Cetip.data import pathandcredentials as pc
from Cetip.utils import utils


def save_excel_file(browser, overwrite=False):
    print("Salvando arquivo")
    try:
        # explore(browser)
        ativos = utils.get_opcoes(browser)
        ativos = utils.clean_list(ativos)
        header_text = []
        header = []
        type_file = ['compromissada', 'volume', 'estoque', 'negocios']
        aux_type = 0
        aux_count = 0
        while aux_type < len(type_file):
            for ativo in ativos:

                filepath = Path(pc.ACT_PATH) / ativo / type_file[aux_type]
                filename = filepath / f"{type_file[aux_type]}-{datetime.now().strftime('%Y%m%d')}"
                if not overwrite and filename.exists():
                    continue
                else:
                    try:
                        #print(pc.BASE_URL.format(pc.ATIVOS_URL[f'{type_file[aux_type]}'].format(ativo)))
                        browser.get(pc.BASE_URL.format(pc.ATIVOS_URL[f'{type_file[aux_type]}'].format(ativo)))
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
                        header_text = browser.find_element(By.CSS_SELECTOR,
                                                           'div.row:nth-child(4) > div:nth-child(1)').find_element(
                            By.TAG_NAME, 'label').text.replace('Observações:', '').split('\n')
                        header.append({
                            'Observações': header_text
                        })
                        _url = browser.find_element(By.CSS_SELECTOR, '.primary-text > a:nth-child(1)').get_attribute(
                            'href')
                        filepath.mkdir(parents=True, exist_ok=True)
                        utils.generate_excel_file(header, _url, filename)
                        aux_count += 1
                        header = []

                    except Exception as e:
                        continue
            print(f'Ativo: {type_file[aux_type]} Quantidade: {aux_count}')
            aux_type += 1
            aux_count = 0
    except Exception as e:
        print(e)

