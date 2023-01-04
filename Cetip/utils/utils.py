from requests import get
from Cetip.data import pathandcredentials as pc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
from datetime import datetime

pattern_int = re.compile(r"(0|-?[1-9][0-9]*)")


def get_safe_setup(remote_url=None, headless=False):
    from selenium import webdriver
    # from seleniumwire import webdriver

    opts = webdriver.FirefoxOptions()
    opts.headless = headless
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-notifications")

    if remote_url is None:
        driver = webdriver.Firefox(options=opts)
    else:
        driver = webdriver.Remote(command_executor=remote_url, options=opts)

    return driver


def clean_list(ativos):
    #Limpar lista de ativos removendo itens inúteis
    aux = 0
    try:
        while aux <= 3:
            for ativo in ativos:
                del ativos[ativo]
                break
            aux += 1
    except Exception as e:
        print(e)
    return ativos


def get_opcoes(browser):
    #Buscar tipos de ativos
    browser.get(pc.BASE_URL.format(pc.ATIVOS_URL['opcoes']))
    options = [e for e in browser.find_element(By.XPATH, "//select[@name='ativo']").find_elements(By.TAG_NAME, 'option') if '-' in e.text]
    return {
        e.get_attribute('value'): e.text for e in options
    }


def set_date_range(browser):
    # Definir range de data
    try:
        print('Alterando data')
        today = datetime.now().strftime("%d/%m/%y")
        today_splited = today.split('/')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(1) > input:nth-child(2)').send_keys(Keys.CONTROL, 'a')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(1) > input:nth-child(2)').send_keys('01')

        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(2) > input:nth-child(2)').send_keys(Keys.CONTROL, 'a')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(2) > input:nth-child(2)').send_keys('01')

        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(3) > input:nth-child(2)').send_keys(Keys.CONTROL, 'a')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(3) > input:nth-child(2)').send_keys('2000')

        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(4) > input:nth-child(2)').send_keys(Keys.CONTROL,'a')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(4) > input:nth-child(2)').send_keys(str(today_splited[0]))

        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(5) > input:nth-child(2)').send_keys(Keys.CONTROL,'a')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(5) > input:nth-child(2)').send_keys(str(today_splited[1]))

        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(6) > input:nth-child(2)').send_keys(Keys.CONTROL,'a')
        browser.find_element(By.CSS_SELECTOR, 'div.large-2:nth-child(6) > input:nth-child(2)').send_keys(str(today_splited[2]))

    except Exception as e:
        print('')


def check_string(str):
    for i in str:
        if i.isalpha():
            return True
        else:
            return False


def check_second_header(browser, header):
    try:
        second_header = [col.text
                         for col in browser.find_element(
                By.CSS_SELECTOR, ".responsive > tbody:nth-child(2) > tr:nth-child(2)"
            ).find_elements(By.TAG_NAME, "td")]
        if any(chr.isdigit() for chr in second_header[0]):
            print("É uma data")
        else:
            header_aux = []
            for data in second_header:
                for old_data in header:
                    if old_data != data:
                        header_aux.append(data)
            if len(header_aux) > 0:
                for dat in header_aux:
                    header.append(dat)
        return second_header
    except Exception as e:
        print(e)


def organize_header(header, header_aux, active_text):
    print('Organizando header')
    new_header = header
    new_header_aux = header_aux
    new_active_text = active_text
    payload = []
    try:
        aux = 0
        while aux <= 3:
            for data in new_header:
                for new_date in new_header_aux:
                    if new_date == data:
                        header.remove(data)
            aux += 1
        new_header = []
        for data in header:
            if ' Financeira' in data or ' Emissão' in data:
                payload.append({data: [{new_header_aux[0].strip():new_active_text[0].strip()}, {new_header_aux[1].strip():new_active_text[1].strip()}]})
                new_header_aux.remove(new_header_aux[0])
                new_header_aux.remove(new_header_aux[0])
                new_active_text.remove(new_active_text[0])
                new_active_text.remove(new_active_text[0])
            elif ' Produto' in data or 'Decorrido' in data:
                payload.append({data: [{new_header_aux[0].strip():new_active_text[0].strip()}, {new_header_aux[1].strip():new_active_text[1].strip()}]})
                new_header_aux.remove(new_header_aux[0])
                new_header_aux.remove(new_header_aux[0])
                new_active_text.remove(new_active_text[0])
                new_active_text.remove(new_active_text[0])
            elif 'Total' in data:
                payload.append({data: [{new_header_aux[0].strip():new_active_text[0].strip()}, {new_header_aux[1].strip():new_active_text[1].strip()}]})
                new_header_aux.remove(new_header_aux[0])
                new_header_aux.remove(new_header_aux[0])
                new_active_text.remove(new_active_text[0])
                new_active_text.remove(new_active_text[0])
            else:
                payload.append({data: new_active_text[0].strip()})
                new_active_text.remove(new_active_text[0])

        return payload
    except Exception as e:
        print(e)


def generate_excel_file(header, _url, filename):
    # Gerar e salvar os dados em um arquivo excel
    try:
        if not filename.exists():
            parse_value = lambda x: f"{x[-4:]}-{x[3:5]}-{x[:2]} " if '/' in x else x.replace(',', '.')
            with open(
                    fr'{filename}.csv','w', newline='') as fp:
                for obs in header:
                    if len(obs) > 0:
                        fp.write('Observações:')
                        for itens in obs.values():
                            for item in itens:
                                if item == ' ':
                                    itens.remove(item)
                                else:
                                    item = item+'\n'
                                    fp.write(item)

                for line in str(get(_url).content, encoding='cp1252').split('\r\n'):
                    if '\t' in line:
                        fp.write(';'.join([parse_value(field) for field in line.split('\t')]) + '\r\n')
                print("Salvando")
        else:
            print("next")
    except Exception as e:
        print(e)
