from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from base import BaseScrapper
from selenium.webdriver.chrome.options import Options
from time import sleep


class NewsRBCScrapper(BaseScrapper):
    """
    Collecting pages urls and texts from rbc.ru
    """

    def __init__(self):
        BaseScrapper.__init__(self)
        self.urls = [
            "https://www.rbc.ru/tags?tag=%D0%91%D0%B8%D0%B7%D0%BD%D0%B5%D1%81",
            "https://www.rbc.ru/tags?tag=%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D1%8B",
            "https://www.rbc.ru/tags?tag=%D0%B4%D0%B5%D0%BD%D1%8C%D0%B3%D0%B8",
            "https://www.rbc.ru/tags?tag=%D0%AD%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8%D0%BA%D0%B0",
            #"https://www.rbc.ru/finances/?utm_source=topline",
            #"https://www.rbc.ru/economics/?utm_source=topline",
        ]

    def get_urls(self):
        def insert_url(url):
            self.session.execute(
                """
                INSERT INTO URLS (url, collected_ts, scrapped)
                VALUES (%s, %s, %s)
                """,
                [url, datetime.now(), False],
                )
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("enable-features=NetworkServiceInProcess")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(100)

        for url_main in self.urls:
            driver.get(url_main)
            end_page = False
            last_len = 0

            try:
                popup = driver.find_element(By.CLASS_NAME, "live-tv-popup__close")
                popup.click()
            except Exception as e:
                print("None popup")
                #self.log(msg=f"Error occured {e}", level="ERROR", source="GET_URLS_RBC")

            urls = set(
                [i.url for i in self.session.execute("SELECT url FROM URLS").all()]
            )
            self.log(
                f"There are {len(urls)} urls already",
                level="INFO",
                source="news_get_urls",
            )

            while not end_page:
                try:
                    objects = driver.find_elements(By.CLASS_NAME, "search-item__link")

                    for obj in objects:
                        u = obj.get_attribute("href")
                        if u not in urls:
                            urls.add(u)
                            insert_url(u)
                            self.log(
                                f"Inserted url {u}. There are {len(urls)} urls already",
                                level="INFO",
                                source="news_get_urls",
                            )

                    if last_len == len(urls):
                        break
                    else:
                        last_len = len(urls)

                except Exception as e:
                    self.log(
                        msg=f"Error occured {e}", level="ERROR", source="GET_URLS_RBC"
                    )
                    driver.quit()

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(self.sleep_time)

        driver.quit()

    def collect(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("enable-features=NetworkServiceInProcess")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)
        urls = [i.url for i in self.session.execute("SELECT url FROM URLS WHERE scrapped = False ALLOW FILTERING").all()]
        self.log(f"Ready to scrapp {len(urls)} urls", level="INFO", source="news_collect")

        for i in range(len(urls)):
            driver.get(urls[i])

            try:
                popup = driver.find_element(By.CLASS_NAME, "live-tv-popup__close")
                popup.click()
            except Exception as e:
                pass
                # self.log(f"Some error during closing popup: {e}", level="ERROR", source="news_collect")

            try:
                text = ""
                objects = driver.find_elements(By.TAG_NAME, "p")
                for obj in objects:
                    text += obj.text
                # attributes
                try:
                    title = driver.find_element(
                        By.XPATH,
                        "/html/body/div[4]/div[1]/div[1]/div[1]/div[2]/div/div[5]/div/div[1]/div[1]/div[1]/div[2]/h1",
                    ).text
                except:
                    title = None
                try:
                    views = driver.find_element(
                        By.XPATH,
                        "/html/body/div[4]/div[1]/div[1]/div[1]/div[2]/div/div[5]/div/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]",
                    ).text
                except:
                    views = None
                try:
                    author = driver.find_element(
                        By.CLASS_NAME, "article__authors__author__name"
                    ).text
                except:
                    author = None
                try:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    sleep(self.sleep_time / 3)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[4]/div[1]/div[1]/div[1]/div[2]/div[1]/div[5]/div/div[1]/div/div[4]/div[1]/div/div/div/div[2]",
                    ).click()
                    keywords = set(
                        [
                            i.text.lower()
                            for i in driver.find_elements(
                                By.CLASS_NAME, "article__tags__item"
                            )
                            if i.text != ""
                        ]
                    )
                except Exception as e:
                    keywords = None
                try:
                    category = driver.find_element(
                        By.CLASS_NAME, "article__header__category"
                    ).text
                except:
                    category = None

                to_insert = [
                    text,
                    urls[i],
                    author,
                    title,
                    int(views.replace(" ", "")) if views else None,
                    datetime.now(),
                    keywords,
                    category,
                ]

                self.session.execute(
                    "INSERT INTO NEWS (news_text, url, author, title, views,"
                    "collected_ts, keywords, category) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    to_insert,
                )
                self.session.execute(
                    "UPDATE URLS SET scrapped = True WHERE url = %s", [urls[i]]
                )

            except Exception as e:
                self.log(
                    f"Error during collecting: {e}",
                    level="ERROR",
                    source="news_collect",
                )

            sleep(self.sleep_time)

            if i % 50 == 0 and i != 0:
                self.log(f"Collected {i} news", level="INFO", source="news_collect")

        driver.quit()
        self.log(f"Collected {len(urls)} news", level="INFO", source="news_collect")

    def test_logs(self):
        self.log("testing logs", level="INFO", source="news_")


if __name__ == "__main__":
    run = NewsRBCScrapper()
    run.get_urls()
    run.collect()

