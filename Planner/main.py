from datetime import datetime

from Planner.controller import planner
from time import sleep
from Planner.utils import utils

if __name__ == '__main__':
    print('abrir browser')
    browser = utils.get_safe_setup(headless=False)
    try:
        print(f'start: {datetime.now()}')
        planner.save_cra(browser)

        print(f'end: {datetime.now()}')

    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
