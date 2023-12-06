from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
from base import BaseScrapper
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep


class NewsRBCScrapper(BaseScrapper):    
    """
    Collecting pages urls and texts from rbc.ru
    """

    def __init__(self):
        BaseScrapper.__init__(self)
        self.urls = ["https://www.rbc.ru/finances/?utm_source=topline",
           "https://www.rbc.ru/economics/?utm_source=topline"]
        self.columns = ["url"]

    def get_urls(self):


        def insert_url(url):
            self.session.execute(
                """
                INSERT INTO URLS (url, collected_ts, scrapped)
                VALUES (%s, %s, %s)
                """, [url, datetime.now(), False]
            )

        driver = webdriver.Chrome()

        for url_main in self.urls:

            driver.get(url_main)
            end_page = False
            sleep_time = 2
            last_len = 0

            try:
                popup = driver.find_element(By.CLASS_NAME, "live-tv-popup__close")
                popup.click()
            except Exception as e:
                self.log(msg=f"Error occured {e}", level="ERROR", source="GET_URLS_RBC")
            
            urls = set()
            
            while not end_page:
                try:
                    objects = driver.find_elements(By.CLASS_NAME, 'item__link')
        
                    for obj in objects:
                        u = obj.get_attribute("href")
                        if u not in urls:
                            urls.add(u)
                            insert_url(u)
                            print(f"inserted url {u}")
                    
                    if last_len == len(urls):
                        break
                    else:
                        last_len = len(urls)

                except Exception as e:
                    self.__log(msg=f"Error occured {e}", level="ERROR", source="GET_URLS_RBC")
                    driver.quit()

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(sleep_time)
        
        driver.quit()
    
    def collect(self):
        
        urls = pd.read_csv(self.path)
        
        driver = webdriver.Chrome()
        texts = []
        urls['text'] = None
            
        for i in range(urls.shape[0]):
            driver.get(urls.loc[i]["url"])
        
            try:
                popup = driver.find_element(By.CLASS_NAME, "live-tv-popup__close")
                popup.click()
            except:
                pass
            
            try:
                text = ''
                objects = driver.find_elements(By.TAG_NAME, "p")
                for obj in objects:
                    text += obj.text
                urls["text"][i] = text
                
            except:
                urls.to_csv(self.path)
                driver.quit()
            sleep(2)
            
            if i % 50 == 0:
                print(f"Collected {i} news")
        
        urls.to_csv(self.path)
        driver.quit()


if __name__ == "__main__":
    run = NewsRBCScrapper()
    run.get_urls()
