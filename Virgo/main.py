from time import sleep
from datetime import datetime
from Virgo.controller import virgo
from Virgo.utils.utils import get_safe_setup

if __name__ == '__main__':
    print('abrir browser')
    browser = get_safe_setup(headless=True)
    try:
        print(f'Inicio: {datetime.now()}')
        virgo.do_login(browser)
        virgo.save_actions(browser)
        print(f'Fim: {datetime.now()}')
    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
