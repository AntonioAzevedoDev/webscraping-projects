from datetime import datetime
from json import dump, load
from pathlib import Path
from time import sleep
from SP_Global.utils import utils
from SP_Global.data import pathandcredentials as pc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def do_login(browser):
    print('login')
    browser.get(pc.LOGIN_URL)
    browser.find_element(By.ID, 'username01').send_keys(pc.LOGIN_USR)
    browser.find_element(By.ID, 'password01').send_keys(pc.LOGIN_PWD)
    browser.find_element(By.CLASS_NAME, 'snl-widgets-input-button').click()
    sleep(3)


def save_press_releases(browser):
    aux_releases = 0
    while aux_releases == 0:
        try:
            print('press releases')
            browser.get(pc.PR_URL)
            utils.accept_cookies(browser)
            browser.find_element(By.ID, 'select2-filter-container').click()
            sleep(1)
            browser.find_element(By.ID, 'select2-filter-result--7').click()
            # browser.find_element(By.ID, 'select2-filter-result--365').click()
            browser.find_element(By.ID, 'select2-countires-container').click()
            sleep(1)
            browser.find_element(By.ID, 'select2-countires-result--BRA').click()
            sleep(1)
            print('atualizar filtro')
            browser.find_element(By.CLASS_NAME, 'button--red').click()
            sleep(3)
            # pagination
            payload = []
            if len(browser.find_elements(By.CLASS_NAME, 'pagination-view')) > 0:
                print('pagination')
                pagination = browser.find_element(By.CLASS_NAME, 'pagination-view')
                pagination.find_elements(By.TAG_NAME, 'li')[-1].click()
                sleep(1)
                pages = browser.find_element(By.CLASS_NAME, 'pagination-v2')
                for page in pages.find_elements(By.TAG_NAME, 'li'):
                    if len(page.find_elements(By.CLASS_NAME, 'disabled')) > 0:
                        continue
                    page.find_element(By.TAG_NAME, 'a').click()
                    sleep(1)
                    # header
                    header = [col.text for col in browser.find_element(By.CLASS_NAME, 'table-module__header').find_elements(By.TAG_NAME, 'li')]
                    # rows
                    body = browser.find_element(By.CLASS_NAME, 'table-module__content')
                    for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                        dte, link = row.find_elements(By.CLASS_NAME, 'table-module__column')
                        payload.append({
                            header[0]: datetime.strptime(dte.text, '%d-%b-%Y %H:%M BRT').strftime('%Y-%m-%d %H:%M:00'),
                            header[1]: link.text,
                            'url': link.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        })
            else:
                # header
                header = [col.text for col in browser.find_element(By.CLASS_NAME, 'table-module__header').find_elements(By.TAG_NAME, 'li')]
                # rows
                body = browser.find_element(By.CLASS_NAME, 'table-module__content')
                for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                    dte, link = row.find_elements(By.CLASS_NAME, 'table-module__column')
                    payload.append({
                        header[0]: datetime.strptime(dte.text, '%d-%b-%Y %H:%M BRT').strftime('%Y-%m-%d %H:%M:00'),
                        header[1]: link.text,
                        'url': link.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    })
            print('salvar')
            filepath = Path(pc.PR_PATH) / f"spr-{datetime.now().strftime('%Y%m%d')}.json"
            with open(filepath, 'w', encoding='utf-8') as fp:
                dump(payload, fp, ensure_ascii=False, indent=1)
            aux_releases = 1
        except Exception as e:
            continue


def save_actions(browser):
    aux_releases = 0
    while aux_releases == 0:
        try:
            print('ratings actions')
            browser.get(pc.ACT_URL)
            utils.accept_cookies(browser)
            # Últimos 7 dias
            browser.find_element(By.CLASS_NAME, 'ratings-filter__radio').find_elements(By.TAG_NAME, 'li')[-1].click()
            sleep(1)
            browser.find_element(By.ID, 'select2-countires-container').click()
            sleep(1)
            browser.find_element(By.ID, 'select2-countires-result--BRA').click()
            sleep(1)
            print('atualizar filtro')
            browser.find_element(By.CLASS_NAME, 'button--red').click()
            sleep(3)
            # TODO: test if pagination needed
            header = [col.text for col in browser.find_element(By.CLASS_NAME, 'table-module__header').find_elements(By.TAG_NAME, 'li')]
            assert len(header) == 10, f'expected 10 cols, got {len(header)}'
            # rows
            payload = []
            body = browser.find_element(By.CLASS_NAME, 'table-module__content')
            for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                entry = row.find_elements(By.CLASS_NAME, 'table-module__column')
                payload.append({
                    header[0]: entry[0].text.replace('\n', '|'),
                    header[1]: entry[1].text,
                    header[2]: utils.br_date(entry[2].text),
                    header[3]: entry[3].text,
                    header[4]: datetime.strptime(entry[4].text, '%d-%b-%Y %H:%M BRT').strftime('%Y-%m-%d %H:%M:00'),
                    header[5] + 'Para': entry[5].text,
                    header[6] + 'Para': entry[6].text,
                    header[7] + 'De': entry[7].text,
                    header[8] + 'De': entry[8].text,
                    header[9]: entry[9].text,
                    'url': entry[0].find_element(By.TAG_NAME, 'a').get_attribute('href')
                })
            print('salvar')
            filepath = Path(pc.ACT_PATH) / f"s-{datetime.now().strftime('%Y%m%d')}.json"
            with open(filepath, 'w', encoding='utf-8') as fp:
                dump(payload, fp, ensure_ascii=False, indent=1)
            aux_releases = 1
        except Exception as e:
            continue


def update_emissores_list(browser):
    aux_releases = 0
    while aux_releases == 0:
        try:
            print('lista de emissores')
            browser.get(pc.RTG_URL)
            utils.accept_cookies(browser)
            payload = []
            segment = browser.find_element(By.CLASS_NAME, 'news__filter')
            for entry in segment.find_elements(By.TAG_NAME, 'li'):
                nome_setor = entry.text
                print(nome_setor)
                assert entry.is_displayed(), 'entry not visible'
                # expand
                entry.click()
                sleep(1)
                # for subentry in entry.find_elements(By.CSS_SELECTOR, "input[name='browseByPractice']"):
                for subentry in entry.find_elements(By.TAG_NAME, 'li'):
                    categoria = subentry.text
                    print(categoria)
                    # browser.execute_script('arguments[0].scrollIntoView();', subentry)
                    # sleep(1)
                    assert subentry.is_displayed(), 'subentry not visible'
                    # subentry.click()
                    radio = subentry.find_element(By.TAG_NAME, 'input')
                    browser.execute_script('arguments[0].click();', radio)
                    sleep(2)
                    ctitle = browser.find_element(By.ID, 'browseByTitle')
                    # browser.execute_script('arguments[0].scrollIntoView();', ctitle)
                    # sleep(1)
                    assert categoria.lower() == ctitle.text.lower(), f'expected {categoria.lower()}, got {ctitle.text.lower()}.'
                    countries = browser.find_element(By.ID, 'select2-countires-container')
                    assert countries.is_displayed(), f'countries not visible'
                    countries.click()
                    sleep(1)
                    browser.find_element(By.ID, 'select2-countires-result--BRA').click()
                    sleep(1)
                    print('atualizar filtro')
                    browser.find_element(By.CLASS_NAME, 'button--red').click()
                    sleep(5)
                    # pagination
                    if len(browser.find_elements(By.CLASS_NAME, 'pagination-view')) > 0:
                        print('pagination')
                        pagination = browser.find_element(By.CLASS_NAME, 'pagination-view')
                        # click max items per page
                        pagination.find_elements(By.TAG_NAME, 'li')[-1].click()
                        sleep(1)
                        assert len(browser.find_element(By.CLASS_NAME, 'paginationjs-pages').find_elements(By.TAG_NAME, 'li')) == 3, 'more pages than expected'
                    # contents
                    body = browser.find_element(By.CLASS_NAME, 'table-module__content')
                    for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                        link = row.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        setor, _, _id = link.split('/')[-3:]
                        payload.append({
                            'entidade': row.text,  # .strip(),
                            'id': _id,
                            'setor': setor.replace('%20', '').lower(),
                            'link': link,
                            'nome_setor': nome_setor,
                            'categoria': categoria.replace('Imobili�ria', 'Imobiliária')
                        })
                # collapse
                entry.click()
                sleep(1)
            print('salvar')
            filepath = Path(pc.RTG_PATH) / f"e-{datetime.now().strftime('%Y%m%d')}.json"
            with open(filepath, 'w', encoding='utf-8') as fp:
                dump(payload, fp, ensure_ascii=False, indent=1)
            aux_releases = 1
        except Exception as e:
            continue


def fetch_emissores(browser, skip_existing=True):
    aux_releases = 0
    while aux_releases == 0:
        try:
            print('fetch emissores')
            with open([p for p in Path(pc.RTG_PATH).glob('*.json')][-1], 'r', encoding='utf-8') as fp:
                source = load(fp)
            utils.accept_cookies(browser)

            for entry in source:
                try:
                    print(entry['entidade'])
                    payload = []
                    setor, _, _id = entry['link'].split('/')[-3:]
                    setor = setor.replace('%20', '').lower()
                    filepath = Path(pc.RTG_PATH) / setor
                    fn = filepath / f"{_id}-{datetime.now().strftime('%Y%m%d')}.json"
                    if skip_existing and fn.exists():
                        continue
                    browser.get(entry['link'])
                    th = WebDriverWait(browser, 30).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'table-module__header'))
                    )
                    WebDriverWait(browser, 30).until(
                        EC.text_to_be_present_in_element(
                            (By.CLASS_NAME, 'headline-3'),
                            entry['entidade']
                        )
                    )

                    page_type = browser.find_element(By.CLASS_NAME, 'breadcumb').find_element(By.TAG_NAME, 'li').text
                    # Rating emissor
                    if 'Ratings' in page_type:
                        try:
                            header = [col.text.lower() for col in th.find_elements(By.TAG_NAME, 'li')]
                            header[3] = header[3].replace('\n', ' ')
                            assert len(header) == 7, f'expected 7 cols, got {len(header)}.'
                            body = browser.find_element(By.CLASS_NAME, 'table-module__content')
                            for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                                cols = row.find_elements(By.CLASS_NAME, 'table-module__column')
                                payload.append({
                                    'entidade': entry['entidade'],
                                    header[0]: cols[0].text,
                                    header[1]: cols[1].text.split('\n')[0],
                                    header[2]: utils.br_date(cols[2].text),
                                    header[3]: utils.br_date(cols[3].text),
                                    header[4]: cols[4].text,
                                    header[5]: cols[5].text,
                                    header[6]: utils.br_date(cols[6].text)
                                })
                        except Exception as e:
                            payload.append({
                                'entidade': '',
                                header[0]: '',
                                header[1]: '',
                                header[2]: '',
                                header[3]: '',
                                header[4]: '',
                                header[5]: '',
                                header[6]: ''
                            })
                    # Rating emissao
                    elif 'Lista' in page_type:
                        try:
                            body = browser.find_element(By.CLASS_NAME, 'table-module__ratings')
                            emissoes = []
                            for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                                emissoes.append({
                                    'emissao': row.text,
                                    'link': row.find_element(By.TAG_NAME, 'a').get_attribute('href')
                                })
                            for emissao in emissoes:
                                browser.get(emissao['link'])
                                th = WebDriverWait(browser, 30).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'table-module__header'))
                                )
                                WebDriverWait(browser, 30).until(
                                    EC.text_to_be_present_in_element(
                                        (By.CLASS_NAME, 'headline-3'),
                                        entry['entidade']
                                    )
                                )
                                header = [col.text.lower() for col in th.find_elements(By.TAG_NAME, 'li')]
                                header[3] = header[3].replace('\n', ' ')
                                assert len(header) == 9, f'expected 9 cols, got {len(header)}.'
                                payload = []
                                body = browser.find_element(By.CLASS_NAME, 'table-module__content')
                                for row in body.find_elements(By.CLASS_NAME, 'table-module__row'):
                                    cols = row.find_elements(By.CLASS_NAME, 'table-module__column')
                                    payload.append({
                                        'entidade': entry['entidade'],
                                        'emissao': emissao['emissao'],
                                        header[0]: cols[0].text,
                                        header[1]: utils.br_date(cols[1].text),
                                        header[2]: cols[2].text,
                                        header[3]: cols[3].text,
                                        header[4]: utils.br_date(cols[4].text),
                                        header[5]: utils.br_date(cols[5].text),
                                        header[6]: cols[6].text,
                                        header[7]: cols[7].text,
                                        header[8]: utils.br_date(cols[8].text)
                                    })
                        except Exception as e:
                            payload.append({
                                'entidade': '',
                                'emissao': '',
                                header[0]: '',
                                header[1]: '',
                                header[2]: '',
                                header[3]: '',
                                header[4]: '',
                                header[5]: '',
                                header[6]: '',
                                header[7]: '',
                                header[8]: ''
                            })

                    filepath.mkdir(parents=True, exist_ok=True)
                    with open(fn, 'w', encoding='utf-8') as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                except Exception as e:
                    payload.append({
                        'entidade': entry['entidade'],
                        header[0]: '',
                        header[1]: '',
                        header[2]: '',
                        header[3]: '',
                        header[4]: '',
                        header[5]: '',
                        header[6]: ''
                    })
                    filepath.mkdir(parents=True, exist_ok=True)
                    with open(fn, 'w', encoding='utf-8') as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    continue
            aux_releases = 1
        except Exception as e:
            continue

