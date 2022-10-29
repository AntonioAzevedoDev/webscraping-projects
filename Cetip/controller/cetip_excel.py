from datetime import datetime
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Cetip.data import pathandcredentials as pc
from Cetip.utils import utils


def save_excel_file(browser, overwrite=False, type_file='volume'):
    print("Salvando arquivo")
    try:
        # explore(browser)
        ativos = utils.get_opcoes(browser)
        print(len(ativos), ativos)
        ativos = utils.clean_list(ativos)
        header_text = []
        header = []
        for ativo in ativos:

            filepath = Path(pc.ACT_PATH) / ativo / type_file
            filename = filepath / f"{type_file}-{datetime.now().strftime('%Y%m%d')}"
            if not overwrite and filename.exists():
                continue
            else:
                try:
                    browser.get(pc.BASE_URL.format(pc.ATIVOS_URL[f'{type_file}'].format(ativo)))
                    sleep(3)

                    utils.set_date_range(browser)
                    if len(browser.find_elements(By.ID, 'header')) > 0:
                        if 'Error' in browser.find_element(By.ID, 'header').text:
                            continue
                    try:
                        browser.find_element(
                            By.CSS_SELECTOR,
                            'a.button:nth-child(2)'
                        ).click()
                        sleep(3)
                    except Exception as e:
                        continue
                    header_text = browser.find_element(By.CSS_SELECTOR,
                                                       'div.row:nth-child(4) > div:nth-child(1)').find_element(
                        By.TAG_NAME, 'label').text.replace('Observações:', '').split('\n')
                    header.append({
                        'Observações': header_text
                    })
                    _url = browser.find_element(By.CSS_SELECTOR, '.primary-text > a:nth-child(1)').get_attribute('href')
                    filepath.mkdir(parents=True, exist_ok=True)
                    utils.generate_excel_file(header, _url, filename)
                    header = []
                except Exception as e:
                    print(e)
                    continue
    except Exception as e:
        print(e)

