from time import sleep
from datetime import datetime
from SP_Global.controller import spglobal as sp
from SP_Global.utils.utils import get_safe_setup

if __name__ == '__main__':
    print('abrir browser')
    browser = get_safe_setup(headless=False)
    try:
        print(f'Inicio: {datetime.now()}')
        sp.do_login(browser)
        #sp.save_press_releases(browser)
        sp.save_actions(browser)
        sp.update_emissores_list(browser)
        sp.fetch_emissores(browser)
        print(f'Fim: {datetime.now()}')
    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
