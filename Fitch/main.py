from datetime import datetime

from controller import fitch
from time import sleep
from Fitch.utils import utils

if __name__ == '__main__':
    print('abrir browser')
    browser = utils.get_safe_setup(headless=True)
    try:
        print(f'start: {datetime.now()}')
        #fitch.save_actions(browser)
        fitch.save_entities(browser)

        print(f'end: {datetime.now()}')

    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
