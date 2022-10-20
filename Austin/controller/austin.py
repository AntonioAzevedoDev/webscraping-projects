from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Austin.utils import utils
from Austin.data import pathandcredentials as pc


def save_ratings(browser, overwrite=False):
    print("ratings actions")
    browser.get(pc.RAT_URL)
    sleep(5)
    header = [col.text for col in
              browser.find_element(By.CSS_SELECTOR, '#UpdatePanel1 > table > thead > tr').find_elements(By.TAG_NAME,'th')]
    assert len(header) == 4, f"expected 4 cols, got {len(header)}"
    payload = []
    filepath = ''
    body = browser.find_element(By.CSS_SELECTOR, "#tableRating > tbody")
    for row in body.find_elements(By.TAG_NAME, "tr"):
        entry = row.find_elements(By.TAG_NAME, "td")
        title = entry[0].text
        url = entry[0].find_element(By.TAG_NAME, "a").get_attribute("href")
        name_file = f"r-{datetime.now().strftime('%Y%m%d')}.json"
        filepath = Path(pc.RAT_PATH) / name_file
        if not overwrite and filepath.exists():
            continue
        else:
            payload.append(
                {
                    header[0]: title,
                    header[1]: entry[1].text,
                    header[2]: entry[2].text,
                    header[3]: entry[3].text,
                    'url': url
                }
            )
    print("salvar")
    with open(filepath, "w", encoding="utf-8") as fp:
        dump(payload, fp, ensure_ascii=False, indent=1)