from datetime import datetime

from controller import austin
from time import sleep
from Austin.utils import utils

if __name__ == '__main__':
    print('abrir browser')
    browser = utils.get_safe_setup(headless=True)
    try:
        print(f'start: {datetime.now()}')
        austin.save_ratings(browser)

        print(f'end: {datetime.now()}')

    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
