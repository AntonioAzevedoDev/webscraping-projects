from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Fitch.utils import utils
from Fitch.data import pathandcredentials as pc


def save_actions(browser):
    print('ratings actions')
    browser.get(pc.ACT_URL)
    sleep(4)
    utils.accept_cookies(browser)
    sleep(2)
    # Validar paginação
    utils.verify_pagination(browser)
    # Fim da validação
    header = [col.text for col in browser.find_element(By.CSS_SELECTOR, 'div.rt-thead:nth-child(1)').find_elements(By.CSS_SELECTOR, 'div.rt-thead:nth-child(1) > div:nth-child(1)')]
    header_splited = header[0].split("\n")
    assert len(header_splited) == 6, f'expected 6 cols, got {len(header_splited)}'
    payload = []
    body = browser.find_element(By.CSS_SELECTOR, '.rt-tbody')
    for row in body.find_elements(By.CLASS_NAME, 'rt-tr-group'):
        entry = row.find_elements(By.CLASS_NAME, 'rt-td')
        payload.append({
            header_splited[0]: utils.br_date(entry[0].text),
            header_splited[1]: entry[1].text,
            header_splited[2]: entry[2].text,
            header_splited[3]: entry[3].text,
            header_splited[4]: entry[4].text,
            header_splited[5]: entry[5].text,
            'url': entry[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
        })
    print('salvar')
    filepath = Path(pc.ACT_PATH) / f"s-{datetime.now().strftime('%Y%m%d')}.json"
    with open(filepath, 'w', encoding='utf-8') as fp:
        dump(payload, fp, ensure_ascii=False, indent=1)


def save_entities(browser):
    print('entities')

    browser.get(pc.ENT_URL)
    sleep(4)
    utils.accept_cookies(browser)
    sleep(2)
    # Validar paginação
    total_pages = utils.verify_pagination_entities(browser)
    # Fim da validação
    if total_pages > 1:
        header = [col.text for col in browser.find_element(By.CSS_SELECTOR, 'div.column__four:nth-child(1)').find_elements(By.CLASS_NAME, 'heading--6')]
        #header_splited = header[0].split("\n")
        assert len(header) == 4, f'expected 4 cols, got {len(header)}'
        payload = []
        header1 = ""
        header3 = ""
        page_now = 1
        aux = 2
        while page_now <= total_pages:
            sleep(1)
            body = browser.find_element(By.CSS_SELECTOR,
                                        '.article > div:nth-child(1) > section:nth-child(2) > div:nth-child(1) > div:nth-child(2)')

            body_len = [col.text for col in browser.find_element(By.CSS_SELECTOR, '.article > div:nth-child(1) > section:nth-child(2) > div:nth-child(1) > div:nth-child(2)').find_elements(By.CSS_SELECTOR, f'div.column__four:nth-child({aux})')]
            if len(body_len) != 0:
                for row in body.find_elements(By.CSS_SELECTOR, f'div.column__four:nth-child({aux})'):
                    #print(f"row {aux}")
                    rating_table = []
                    i = 2

                    while len(rating_table) == 0:

                        try:
                            rating_table = ['-']

                        except Exception as ex:
                            continue
                        try:
                            #rating_table = [col.text for col in row.find_element(By.CSS_SELECTOR,f'div.column__four:nth-child({aux}) > div:nth-child(2) > p:nth-child(1)')]
                            rating_table = [col.text for col in row.find_element(By.CSS_SELECTOR,f'div.column__four:nth-child({aux}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1)').find_elements(By.TAG_NAME, 'td')]
                            sector_and_country_table = [col.text for col in row.find_element(By.CSS_SELECTOR,f'div.column__four:nth-child({aux}) > div:nth-child(3)').find_elements(By.TAG_NAME, 'p')]
                            analyst_table = [col.text for col in row.find_element(By.CSS_SELECTOR,f'div.column__four:nth-child({aux}) > div:nth-child(4)').find_elements(By.TAG_NAME, 'p')]
                        except Exception as ex:
                            continue
                        i += 1
                    aux_skip = 0
                    aux_take = 4

                    while aux_skip <= len(rating_table):
                        if aux_take > len(rating_table):
                            break
                        rating_elements = rating_table[aux_skip:aux_take]

                        try:
                            header1 += "\n" + rating_elements[0] + "\n " + rating_elements[1] + "\n " + rating_elements[2] + "\n " + rating_elements[3]

                            aux_skip += 4
                            aux_take += 4
                        except Exception as e:
                            continue

                    aux_skip = 0
                    aux_take = 2
                    while aux_skip <= len(analyst_table):
                        if aux_take > len(analyst_table):
                            break
                        analyst_elements = analyst_table[aux_skip:aux_take]
                        try:
                            header3 += "\n" + analyst_elements[0] + "\n " + rating_elements[1]

                            aux_skip += 2
                            aux_take += 2
                        except Exception as e:
                            continue
                    entity_name = row.text.split("\n")
                    if entity_name[0] == 'ULTIMATE PARENT':
                        entity_name[0] = entity_name[1]
                    payload.append({
                        header[0]: entity_name[0],
                        header[1]: header1,
                        header[2]: sector_and_country_table[0],
                        header[3]: header3,
                        'url': row.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    })
                    if aux != 25:
                        aux += 1
                        header1 = ""
                        header3 = ""
                        sector_and_country_table = ['-']
                        sleep(1)
                    else:
                        #Mudar de página
                        page_now += 1
                        list_buttons = browser.find_element(By.CSS_SELECTOR,'.pager__items')
                        for button in list_buttons.find_elements(By.TAG_NAME, 'li'):
                            try:
                                if int(button.text) == page_now:
                                    button.click()
                                    list_buttons = []
                                    break
                            except Exception as e:
                                continue

                        aux = 2

                        header1 = ""
                        header3 = ""
                        sector_and_country_table = ['-']
                        sleep(5)
                        print(f"Page: {page_now}")
            else:
                page_now += 1
                break
        print('salvar')

        filepath = Path(pc.ENT_PATH) / f"s-{datetime.now().strftime('%Y%m%d')}.json"
        with open(filepath, 'w', encoding='utf-8') as fp:
            dump(payload, fp, ensure_ascii=False, indent=1)
