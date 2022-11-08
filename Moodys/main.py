from time import sleep
from Moodys.utils import utils
from Moodys.controller import moody


if __name__ == '__main__':
    print('abrir browser')
    browser = utils.get_safe_setup(headless=False)
    try:
        moody.save_releases(browser)
        moody.save_ratings(browser)
    except Exception as e:
        print(e)
        sleep(10)
    finally:
        browser.quit()
