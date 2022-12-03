from datetime import datetime

from Canal_Securitizadora.controller import canal_securitizadora
from time import sleep
from Canal_Securitizadora.utils import utils

if __name__ == '__main__':
    print('abrir browser')
    browser = utils.get_safe_setup(headless=False)
    try:
        print(f'start: {datetime.now()}')
        canal_securitizadora.save_cra(browser)

        print(f'end: {datetime.now()}')

    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
