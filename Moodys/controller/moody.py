from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Moodys.utils import utils
from Moodys.data import pathandcredentials as pc

def save_releases(browser):
    print('press releases')
    browser.get(pc.REL_URL)
    sleep(4)
    utils.accept_terms_and_conditions(browser)
    sleep(2)

    header = [col.text for col in browser.find_element(By.CSS_SELECTOR, '.ml-table > tbody:nth-child(1)').find_elements(By.TAG_NAME, 'td')]
    header_splited = [header[0], header[1], header[2]]

    assert len(header_splited) == 3, f'expected 3 cols, got {len(header)}'

    payload = []
    body = browser.find_element(By.CSS_SELECTOR, '.ml-table > tbody:nth-child(1)')
    for row in body.find_elements(By.TAG_NAME, 'tr'):
        entry = row.find_elements(By.TAG_NAME, 'td')
        try:
            payload.append({
                header_splited[0]: entry[0].text,
                header_splited[1]: utils.br_date(entry[1].text),
                'Url_file': entry[2].find_element(By.TAG_NAME, 'a').get_attribute('href')
            })
        except Exception as e:
            print(e)

    print('salvar')
    filepath = Path(pc.REL_PATH) / f"s-{datetime.now().strftime('%Y%m%d')}.json"
    with open(filepath, 'w', encoding='utf-8') as fp:
        dump(payload, fp, ensure_ascii=False, indent=1)


