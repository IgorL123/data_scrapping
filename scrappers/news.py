from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import traceback
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from time import sleep


class Scrapper:
    """
    Collecting pages urls and texts from rbc.ru
    """
    def __init__(self, base_url, max_volume, save_path):
        self.url = base_url
        self.max_vol = max_volume
        self.path = save_path
        self.dtf = pd.DataFrame(columns=[
            "url"
        ])
    
    def get_urls(self):
        num = self.max_vol
        
        driver = webdriver.Chrome()
        driver.get(self.url)
        
        try:
            popup = driver.find_element(By.CLASS_NAME, "live-tv-popup__close")
            popup.click()
        except:
            pass
        
        urls = []
        
        while num:
            try:
                objects = driver.find_elements(By.CLASS_NAME, 'item__link')
                url = []
                for obj in objects:
                    urls.append(obj.get_attribute("href"))
                
                num -= 1
            except Exception as er:
                print(er)
                driver.quit()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"INFO collected {len(urls)} urls")
            sleep(9)
        
        self.dtf = pd.concat([self.dtf, pd.DataFrame(urls, columns=["url"])], ignore_index=True)
        
        driver.quit()
        self.save()
        
    def extract(self):
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
    
    def save(self):
        self.dtf.to_csv(self.path)
