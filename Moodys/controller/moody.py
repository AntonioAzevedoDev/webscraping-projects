from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Moodys.utils import utils
from Moodys.data import pathandcredentials as pc
import operator


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


def save_ratings(browser, overwrite = False):
    print('ratings')
    categories = ['corp', 'strfin', 'finance', 'infraprojects', 'insurance', 'subsov']
    for category in categories:
        filepath = Path(pc.RAT_PATH)
        filename = filepath / f"{category}-{datetime.now().strftime('%Y%m%d')}.json"
        if not overwrite and filename.exists():
            continue
        else:
            browser.get(pc.RAT_URL+category)
            sleep(4)
            utils.accept_terms_and_conditions(browser)
            sleep(2)

            header = [col.text for col in browser.find_element(By.CSS_SELECTOR, '.ml-table > tbody:nth-child(1) > tr:nth-child(1)').find_elements(By.TAG_NAME, 'td')]

            assert len(header) == 8, f'expected 8 cols, got {len(header)}'

            payload = []
            body = browser.find_element(By.CSS_SELECTOR, '.ml-table > tbody:nth-child(1)')
            for row in body.find_elements(By.TAG_NAME, 'tr'):
                entry = row.find_elements(By.TAG_NAME, 'td')
                if 'Emissor' in entry[0].text:
                    continue
                else:
                    url_report = ''
                    url_last_report = ''
                    try:
                        url_report = entry[5].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    except Exception as e:
                        url_report = ''
                    try:
                        url_last_report = entry[6].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    except Exception as e:
                        url_last_report = ''
                    try:
                        try:
                            payload.append({
                                header[0]: entry[0].text,
                                header[1]: entry[1].text,
                                header[2]: entry[2].text,
                                header[3]: entry[3].text,
                                header[4]: utils.br_date(entry[4].text),
                                header[5]: url_report,
                                header[6]: url_last_report,
                                header[7]: entry[7].text
                            })
                        except Exception as e:
                            payload.append({
                                header[0]: entry[0].text,
                                header[1]: entry[1].text,
                                header[2]: entry[2].text,
                                header[3]: entry[3].text,
                                header[4]: utils.br_date(entry[4].text),
                                header[5]: url_report,
                                header[6]: url_last_report,
                                header[7]: entry[7].text
                            })
                    except Exception as e:
                        last_element = operator.itemgetter(-1)(payload)
                        try:
                            last_element['Tipo de Rating'] = (last_element['Tipo de Rating'] + '\n' + entry[0].text).split('\n')
                            last_element['Ratings'] = (last_element['Ratings'] + '\n' + entry[1].text).split('\n')
                        except Exception as f:
                            last_element['Tipo de Rating'].append(entry[0].text)
                            last_element['Ratings'].append(entry[1].text)

            print('salvar')
            filepath.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as fp:
                dump(payload, fp, ensure_ascii=False, indent=1)


