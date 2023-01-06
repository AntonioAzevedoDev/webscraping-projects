from datetime import datetime
from time import sleep
from Cetip.controller import cetip_excel
from Cetip.utils import utils


def run():
    print('abrir browser')
    # browser = utils.get_safe_setup(remote_url='192.168.20.118:4444', headless=True)
    browser = utils.get_safe_setup(remote_url=None, headless=False)
    try:
        print(f'start: {datetime.now()}')
        # cetip.get_data(browser)
        # cetip.save_volume_information(browser)
        cetip_excel.save_excel_file(browser)
        print(f'end: {datetime.now()}')
    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()


if __name__ == '__main__':
    run()

