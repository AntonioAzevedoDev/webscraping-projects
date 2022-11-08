from datetime import datetime
from json import dump
from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Fitch.utils import utils
from Fitch.data import pathandcredentials as pc


def save_actions(browser, overwrite=False):
    print("ratings actions")
    browser.get(pc.ACT_URL)
    sleep(5)
    utils.accept_cookies(browser)
    sleep(2)
    utils.verify_pagination(browser)
    header_splited = utils.return_header_splited(browser)
    assert len(header_splited) == 6, f"expected 6 cols, got {len(header_splited)}"
    payload = []
    url_list = []
    body = browser.find_element(By.CSS_SELECTOR, ".rt-tbody")
    for row in body.find_elements(By.CLASS_NAME, "rt-tr-group"):
        entry = row.find_elements(By.CLASS_NAME, "rt-td")
        header_splited = utils.return_header_splited(browser)
        title = entry[1].text
        url = entry[1].find_element(By.TAG_NAME, "a").get_attribute("href")
        dte = utils.br_date(entry[0].text)
        commentary_file = ""
        if len(url) > 0:
            commentary_file = f"{utils.hashed(title)}-{utils.nods(dte)}.html"
            url_list.append(url + "@" + commentary_file)
        payload.append(
            {
                header_splited[0]: dte,
                header_splited[1]: entry[1].text,
                header_splited[2]: entry[2].text.split("\n"),
                header_splited[3]: entry[3].text.split("\n"),
                header_splited[4]: entry[4].text,
                header_splited[5]: entry[5].text.split("\n"),
                "commentary": commentary_file,
            }
        )
    print("salvar")
    Path(pc.ACT_PATH).mkdir(parents=True, exist_ok=True)
    filepath = Path(pc.ACT_PATH) / f"s-{datetime.now().strftime('%Y%m%d')}.json"
    with open(filepath, "w", encoding="utf-8") as fp:
        dump(payload, fp, ensure_ascii=False, indent=1)
    save_action_commentary(browser, url_list, overwrite)


def save_action_commentary(browser, url_list, overwrite=False):
    print("rating action commentary")
    try:
        for url in url_list:
            _url, file_name = url.split("@")
            Path(pc.COM_PATH).mkdir(parents=True, exist_ok=True)
            filepath = Path(pc.COM_PATH) / file_name
            if not overwrite and filepath.exists():
                continue
            browser.get(_url)
            sleep(4)
            payload = []
            try:
                with open(filepath, "w") as arquivo:
                    title = WebDriverWait(browser, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.heading--1'))
                    ).text
                    body = browser.find_element(By.CSS_SELECTOR, ".RAC")
                    for row in body.find_elements(By.TAG_NAME, f"p"):
                        payload.append(row.text)
                    payload.insert(0, title)
                    for line in payload:
                        arquivo.write(line)
            except Exception as e:
                print(e)
            sleep(2)

    except Exception as e:
        print(e)


def save_entities(browser, overwrite=False):
    print("entities")
    url_list = [""]
    browser.get(pc.ENT_URL)
    sleep(4)
    utils.accept_cookies(browser)
    sleep(1)
    total_pages = utils.verify_pagination_entities(browser)
    Path(pc.ENT_PATH).mkdir(parents=True, exist_ok=True)
    if total_pages > 1:
        header = [
            col.text
            for col in browser.find_element(
                By.CSS_SELECTOR, "div.column__four:nth-child(1)"
            ).find_elements(By.CLASS_NAME, "heading--6")
        ]
        assert len(header) == 4, f"expected 4 cols, got {len(header)}"
        payload = []
        header1 = ""
        header3 = ""
        page_now = 1
        aux = 2
        analyst_table = []
        i = 2
        while page_now <= total_pages:
            try:
                sleep(1)
                body = browser.find_element(
                    By.CSS_SELECTOR,
                    ".article > div:nth-child(1) > section:nth-child(2) > div:nth-child(1) > div:nth-child(2)",
                )

                body_len = [
                    col.text
                    for col in browser.find_element(
                        By.CSS_SELECTOR,
                        ".article > div:nth-child(1) > section:nth-child(2) > div:nth-child(1) > div:nth-child(2)",
                    ).find_elements(By.CSS_SELECTOR, f"div.column__four:nth-child({aux})")
                ]
                if len(body_len) != 0:
                    for row in body.find_elements(
                        By.CSS_SELECTOR, f"div.column__four:nth-child({aux})"
                    ):
                        url = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                        url_splited = utils.return_url_splited(url)
                        url_code = url_splited.pop()
                        name_file = f"{utils.hashed(url_code)}-{datetime.now().strftime('%Y%m%d')}.json"

                        filepath = Path(pc.ENT_PATH) / name_file
                        if not overwrite and filepath.exists():
                            aux += 1
                            continue
                        else:
                            rating_table = []

                            aux_detais = 0
                            while len(rating_table) == 0:

                                try:
                                    rating_table = ["-"]

                                except Exception as ex:
                                    continue
                                try:
                                    rating_table = [
                                        col.text
                                        for col in row.find_element(
                                            By.CSS_SELECTOR,
                                            f"div.column__four:nth-child({aux}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2)",
                                        ).find_elements(By.TAG_NAME, "td")
                                    ]
                                    rating_table_detailed = row.find_element(
                                        By.CSS_SELECTOR,
                                        f"div.column__four:nth-child({aux}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2)",
                                    ).find_elements(By.TAG_NAME, "td")

                                    for details in rating_table_detailed:
                                        try:
                                            try:
                                                prefix = details.find_element(
                                                    By.TAG_NAME, f"span"
                                                ).get_attribute("class")
                                                if prefix != "":
                                                    rating_table[aux_detais] = (
                                                        rating_table[aux_detais]
                                                        + ","
                                                        + prefix
                                                    )
                                                else:
                                                    rating_table[aux_detais] = (
                                                        rating_table[aux_detais] + ","
                                                    )
                                                aux_detais += 1
                                            except Exception as e:
                                                aux_detais += 1
                                                continue

                                        except Exception as e:
                                            continue

                                except Exception as ex:
                                    rating_table = ["-"]

                            sector_and_country_table = [
                                col.text
                                for col in row.find_element(
                                    By.CSS_SELECTOR,
                                    f"div.column__four:nth-child({aux}) > div:nth-child(3)",
                                ).find_elements(By.TAG_NAME, "p")
                            ]
                            analyst_table = [
                                col.text
                                for col in row.find_element(
                                    By.CSS_SELECTOR,
                                    f"div.column__four:nth-child({aux}) > div:nth-child(4)",
                                ).find_elements(By.TAG_NAME, "p")
                            ]

                            aux_skip = 0
                            aux_take = 4

                            while aux_skip <= len(rating_table):
                                if aux_take > len(rating_table):
                                    break
                                rating_elements = rating_table[aux_skip:aux_take]

                                try:
                                    header1 += (
                                        rating_elements[0]
                                        + ","
                                        + rating_elements[1]
                                        + ","
                                        + rating_elements[2]
                                        + ","
                                        + rating_elements[3]
                                        + "\n"
                                    )
                                    aux_skip += 4
                                    aux_take += 4
                                except Exception as e:
                                    continue
                            header1_splited = header1.strip().split("\n")
                            aux_skip = 0
                            aux_take = 2
                            try:
                                while aux_skip <= len(analyst_table):
                                    if aux_take > len(analyst_table):
                                        break
                                    analyst_elements = analyst_table[aux_skip:aux_take]

                                    if header3 != "":
                                        header3 += (
                                            ","
                                            + analyst_elements[0]
                                            + ","
                                            + analyst_elements[1]
                                        )
                                    else:
                                        header3 += (
                                            analyst_elements[0] + "\n" + analyst_elements[1]
                                        )

                                    aux_skip += 2
                                    aux_take += 2
                            except Exception as e:
                                print(e)
                            header3_splited = header3.strip().split("\n")
                            entity_name = row.text.split("\n")
                            if entity_name[0] == "ULTIMATE PARENT":
                                entity_name[0] = entity_name[1]
                            sector_and_country_table_splited = (
                                sector_and_country_table[0].strip().split("\n")
                            )
                            sector_and_country_table_splited = [
                                element
                                for element in sector_and_country_table_splited
                                if element.strip()
                            ]
                            payload.append(
                                {
                                    header[0]: entity_name[0],
                                    header[1]: header1_splited,
                                    header[2]: sector_and_country_table_splited,
                                    header[3]: header3_splited,
                                    "url": row.find_element(By.TAG_NAME, "a").get_attribute(
                                        "href"
                                    ),
                                }
                            )
                            with open(filepath, "w", encoding="utf-8") as fp:
                                dump(payload, fp, ensure_ascii=False, indent=1)
                            url_list.append(url + "@" + name_file)
                            payload = []

                        if aux != 25:
                            aux += 1
                            header1 = ""
                            header3 = ""
                            sector_and_country_table = [""]
                            sleep(1)
                        else:
                            # Mudar de página
                            page_now += 1
                            list_buttons = browser.find_element(
                                By.CSS_SELECTOR, ".pager__items"
                            )
                            for button in list_buttons.find_elements(By.TAG_NAME, "li"):
                                try:
                                    if int(button.text) == page_now:
                                        button.click()
                                        list_buttons = []
                                        break
                                except Exception as e:
                                    continue

                            aux = 2

                            header1 = ""
                            header3 = ""
                            sector_and_country_table = [""]
                            sleep(4)
                            print(f"Page: {page_now}")

                else:
                    page_now += 1
                    break
            except Exception as e:
                continue
    save_securities_and_obligations(browser, url_list, overwrite)


def save_securities_and_obligations(browser, url_list, overwrite=False):
    print("securities and obligations")
    aux_save = 0

    try:
        url_list.remove("")
    except Exception as e:
        print("Lista limpa!")
    while aux_save < len(url_list):
        try:
            print(f"Tamanho da lista {len(url_list)}")
            for url in url_list:
                _url, file_name = url.split("@")
                Path(pc.SEC_PATH).mkdir(parents=True, exist_ok=True)
                filepath = Path(pc.SEC_PATH) / file_name
                if not overwrite and filepath.exists():
                    continue
                else:
                    browser.get(_url)
                    sleep(5)
                    payload = []
                    table_rows = []
                    section = WebDriverWait(browser, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.main > article:nth-child(1)'))
                    ).find_elements(By.TAG_NAME, f"section")
                    sleep(1)

                    for line in section:
                        try:
                            row_id = line.get_attribute("id")
                            if row_id != "" and row_id == "securities-and-obligations":
                                break
                        except Exception as e:
                            row_id = ""
                    try:
                        body = browser.find_element(
                            By.CSS_SELECTOR, "div.rt-tbody:nth-child(3)"
                        )
                        for row in body.find_elements(By.CLASS_NAME, "rt-tr-group"):

                            if row_id == "securities-and-obligations":
                                try:
                                    header_list = (
                                        browser.find_element(
                                            By.CSS_SELECTOR,
                                            ".ReactTable > div:nth-child(1)",
                                        )
                                        .find_element(
                                            By.CSS_SELECTOR,
                                            ".ReactTable > div:nth-child(1) > div:nth-child(1)",
                                        )
                                        .text.split("\n")
                                    )
                                    SAO_table = [
                                        col.text
                                        for col in row.find_elements(
                                            By.CLASS_NAME, "rt-td"
                                        )
                                    ]
                                    SAO_table_splited = SAO_table
                                    aux = 0
                                    aux_table = 0
                                    for sao in SAO_table:
                                        SAO_table_splited[aux] = sao.split("\n")
                                        aux += 1
                                except Exception as e:
                                    print(e)
                                aux_span = 0

                                try:
                                    row_elements = row.find_elements(
                                        By.CLASS_NAME, "rt-td"
                                    )
                                    class_name = row_elements[1].find_elements(
                                        By.TAG_NAME, f"span"
                                    )
                                    if len(class_name) == 1:
                                        while aux_span <= len(class_name):
                                            class_attribute_name = class_name[
                                                aux_span
                                            ].get_attribute("class")
                                            if (
                                                class_attribute_name != ""
                                                and class_attribute_name
                                                != "link--1 link--3"
                                            ):
                                                break
                                            aux_span += 1
                                    else:
                                        while aux_span <= (len(class_name)-1):
                                            class_attribute_name = class_name[
                                                aux_span
                                            ].get_attribute("class")
                                            if (
                                                class_attribute_name != ""
                                                and class_attribute_name
                                                != "link--1 link--3"
                                            ):
                                                break
                                            aux_span += 1
                                except Exception as e:
                                    continue
                                if (
                                    class_attribute_name != ""
                                    and class_attribute_name != "link--1 link--3"
                                ):
                                    temporary_table = SAO_table_splited[aux_span]
                                    temporary_table[1] = (
                                        temporary_table[1] + "," + class_attribute_name
                                    )
                                    SAO_table_splited[aux_span] = temporary_table
                                    class_attribute_name = ""
                                    aux_table += 1
                                table_rows.append(
                                    {
                                        header_list[0]: SAO_table_splited[0],
                                        header_list[1]: SAO_table_splited[1],
                                        header_list[2]: SAO_table_splited[2],
                                        header_list[3]: SAO_table_splited[3],
                                        header_list[4]: SAO_table_splited[4],
                                    }
                                )
                    except Exception as e:
                        payload.append({"seção": [""], "url": url})

                    if table_rows != []:
                        payload.append({"seção": table_rows, "url": url})
                    if payload == []:
                        payload.append({"seção": [""], "url": url})
                    with open(filepath, "w", encoding="utf-8") as fp:
                        dump(payload, fp, ensure_ascii=False, indent=1)
                    aux_save += 1
        except Exception as e:
            aux_save += 1
