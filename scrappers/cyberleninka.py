from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from base import BaseScrapper
from time import sleep


class CyberScrapper(BaseScrapper):
    """
    Collecting pages urls and texts from cyberleninka.ru
    """

    def __init__(self):
        BaseScrapper.__init__(self)
        self.url = "https://cyberleninka.ru/article/c/economics-and-business"

    def collect(self):
        sleeping_time = 20
        options = Options()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": self.get_new_ua()}
        )

        try:
            num_page = (
                self.session.execute("SELECT max(num_page) as num_page FROM CLPAPERS")
                .one()
                .num_page
            )
            last_id = (
                self.session.execute("SELECT max(id) as id FROM CLPAPERS").one().id
            )

        except Exception as e:
            print(e)

        if not last_id:
            last_id = 0

        #self.session.execute("DELETE FROM CLPAPERS WHERE num_page = %s", [num_page])

        num_page += 1
        self.log(f"Start scrapping from page {num_page}", level="INFO", source="papers_collect")
        if num_page:
            driver.get(self.url + f"/{num_page}")
        else:
            driver.get(self.url)

        # num of li elements on the page
        last_paper_on_page = -7
        if not num_page:
            num_page = 1
        num = 25

        try:
            while num:
                elements = driver.find_elements(By.TAG_NAME, "li")
                articles = elements[:last_paper_on_page]
                next_page = self.url + f"/{num_page + 1}"
                num -= 1

                for article in articles:
                    href = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                    driver.get(href)

                    objects = driver.find_elements(By.TAG_NAME, "p")

                    # get text of paper
                    text = ""
                    for obj in objects:
                        text += obj.text

                    # attributes
                    try:
                        author = driver.find_element(By.CLASS_NAME, "hl").text
                    except:
                        author = None
                    try:
                        views = driver.find_element(
                            By.CLASS_NAME, "statitem.views"
                        ).text
                    except:
                        views = None
                    try:
                        down = driver.find_element(
                            By.CLASS_NAME, "statitem.downloads"
                        ).text
                    except:
                        down = None
                    try:
                        likes = driver.find_element(By.CLASS_NAME, "likes").text.split(
                            "\n"
                        )
                    except:
                        likes = [None, None]
                    try:
                        year = (
                            driver.find_element(By.CLASS_NAME, "label.year")
                            .find_element(By.TAG_NAME, "time")
                            .text
                        )
                    except:
                        year = None
                    try:
                        journal = (
                            driver.find_element(By.CLASS_NAME, "half")
                            .find_elements(By.TAG_NAME, "a")[-1]
                            .text
                        )
                    except:
                        journal = None
                    try:
                        words = set(
                            [
                                i.text
                                for i in driver.find_element(
                                    By.CLASS_NAME, "full.keywords"
                                ).find_elements(By.CLASS_NAME, "hl.to-search")
                            ]
                        )
                    except:
                        words = None
                    try:
                        title = driver.find_element(By.TAG_NAME, "i").text
                    except:
                        title = None
                    last_id += 1

                    lst = [
                        last_id,
                        href,
                        author,
                        datetime.now(),
                        int(likes[1]) if likes[1] else None,
                        journal,
                        int(likes[0]) if likes[0] else None,
                        text,
                        num_page,
                        title,
                        int(year) if year else None,
                        words,
                        int(views) if views else None,
                        int(down) if down else None,
                    ]
                    self.session.execute(
                        """
                                        INSERT INTO CLPAPERS ( 
                                            id, 
                                            url, author, collected_ts, 
                                            dislikes, journal, likes, 
                                            paper_text, num_page, title,
                                            year, keywords, views, downloads)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        """,
                        lst,
                    )
                    sleep(sleeping_time)
                    driver.back()

                self.log(f"Saved {num * 20} papers", source="cyber_leninka")

                driver.execute_cdp_cmd(
                    "Network.setUserAgentOverride", {"userAgent": self.get_new_ua()}
                )
                driver.get(next_page)
                num_page += 1

        except Exception as ex:
            self.log(f"Some error occured: {ex}", level="ERROR", source="cyber_leninka")
            driver.quit()


if __name__ == "__main__":
    run = CyberScrapper()
    run.collect()
