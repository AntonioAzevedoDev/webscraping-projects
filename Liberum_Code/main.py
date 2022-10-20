from datetime import datetime

from Liberum.controller import liberum
from time import sleep
from Liberum.utils import utils


if __name__ == '__main__':

    print('abrir browser')
    browser = utils.get_safe_setup(headless=True)
    try:
        print(f'start: {datetime.now()}')
        liberum.save_ratings(browser)
        print(f'end: {datetime.now()}')

    except Exception as e:
        print(e)
        sleep(10)
    finally:
        #browser.quit()
        print('Fim')