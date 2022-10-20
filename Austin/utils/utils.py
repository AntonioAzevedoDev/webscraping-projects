from datetime import datetime
import hashlib

from Austin.data import pathandcredentials as pc


nods = lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%Y%m%d')
hashed = lambda x: hashlib.md5(f'{x}'.encode('utf-8')).hexdigest()


def get_safe_setup(headless=False):
    from selenium import webdriver
    from selenium_stealth import stealth

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options,
                              executable_path=pc.DRI_PATH)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver
