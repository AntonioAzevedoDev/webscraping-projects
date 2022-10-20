from json import dump
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from Liberum.utils import utils
from Liberum.data import pathandcredentials as pc



def save_ratings(browser, overwrite=False):
    print("ratings")
    browser.get(pc.RAT_URL)
    sleep(4)
    # VALIDAR PAGINAÇÃO
    total_pages = utils.verify_pagination(browser)
    # Fim validação
    aux_header = 1
    header = []
    repetidos = 0
    while aux_header <= 7:
        try:
            header.append(browser.find_element(
                By.CSS_SELECTOR, "#tbl-contact > thead:nth-child(1) > tr:nth-child(1)"
            ).find_element(By.CSS_SELECTOR, f"th.sorting_disabled:nth-child({aux_header})").text)
            aux_header += 1
        except Exception as e:
            continue
    print("")
    assert len(header) == 7, f"expected 7 cols, got {len(header)}"
    payload = []

    page_now = 1
    while page_now <= total_pages:
        try:
            body = browser.find_element(By.CSS_SELECTOR, "tbody.table-striped")
            header = [
                col.text
                for col in browser.find_element(
                    By.CSS_SELECTOR, "#tbl-contact > thead:nth-child(1) > tr:nth-child(1)"
                ).find_elements(By.TAG_NAME, "th")
            ]
            aux = 1
            for row in body.find_elements(By.TAG_NAME, "tr"):
                expand_rating(row, aux)
                body = browser.find_element(By.CSS_SELECTOR, "tbody.table-striped")
                entry = row.find_elements(By.TAG_NAME, "td")
                name_file = entry[1].text
                try:
                    url_pdf = body.find_element(
                        By.CSS_SELECTOR,
                        f".dtr-details > li:nth-child(6) > span:nth-child(2) > a:nth-child(2)",
                    ).get_attribute("href")
                except Exception as e:
                    url_pdf = ""

                name_file = name_file + ".json"
                filepath = Path(pc.RAT_PATH) / name_file
                if not overwrite and filepath.exists():
                    expand_rating(row, aux)
                    payload = []
                    aux += 1
                    repetidos += 1
                    continue
                else:
                    entry = row.find_elements(By.TAG_NAME, "td")
                    description_item = []
                    description_attribute = []
                    description_list = []
                    for description in body.find_elements(By.CSS_SELECTOR, "td.child"):
                        description_list = description.find_elements(By.TAG_NAME, "li")

                    for item in description_list:
                        aux_attribute = 1
                        attribute_list = item.text.split('\n')
                        if attribute_list[0] == 'News Release':
                            break
                        while aux_attribute < len(attribute_list):
                            if attribute_list[aux_attribute] == '':
                                aux_attribute += 1
                                continue
                            else:
                                description_attribute.append(attribute_list[aux_attribute])
                                aux_attribute += 1
                        description_item.append({
                            attribute_list[0]: description_attribute
                        })
                        description_attribute = []

                    payload.append(
                        {
                            header[0]: utils.br_date(entry[0].text),
                            header[1]: entry[1].text,
                            header[2]: entry[2].text.split("\n"),
                            header[3]: entry[3].text.split("\n"),
                            header[4]: entry[4].text.split("\n"),

                        }
                    )
                    for item in description_item:
                        payload.append(item)
                    payload.append({"Url_PDF": url_pdf})
                    expand_rating(row, aux)
                    print("salvar")

                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    payload = []
                    aux += 1
            # Next page
            try:
                browser.find_element(
                    By.CSS_SELECTOR, "#tbl-contact_next > a:nth-child(1)"
                ).click()
                page_now += 1
                print(f"page: {page_now}")
                aux = 1
            except Exception as e:
                print("Sem mais paginas!")
                print(f"Quantidade de ID's repetidos {repetidos}")
                page_now += 1

            sleep(1)
        except Exception as e:
            continue


def expand_rating(row, aux):
    try:
        row.find_element(
            By.CSS_SELECTOR, f"tr.odd:nth-child({aux}) > td:nth-child(1)"
        ).click()
        sleep(1)
    except Exception as e:
        row.find_element(
            By.CSS_SELECTOR, f"tr.even:nth-child({aux}) > td:nth-child(1)"
        ).click()
        sleep(1)