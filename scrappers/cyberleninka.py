from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import traceback
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from time import sleep


class CyberScrapper:
    """
    Collecting pages urls and texts from cyberleninka.ru
    """
    def __init__(self, base_url, max_volume, save_path, num_page=None):
        self.url = base_url
        self.max_vol = max_volume
        self.path = save_path
        self.num_page = num_page
        self.columns = ["url", "author", "title", "text", "year", "labels", "views", 
                                          "downloads", "likes", "dislikes", "journal"]
        self.data = pd.DataFrame(columns=self.columns)
        
    def get(self):
        
        ua = UserAgent()
        user_agent = ua.random
        
        driver = webdriver.Chrome()
        
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
        if self.num_page:
            driver.get(self.url + f"/{self.num_page}")
        else:
            driver.get(self.url)
        num = self.max_vol
        
        # num of li elements on the page
        last_paper_on_page = -7
        if self.num_page:
            page_num = self.num_page
        else:
            page_num = 2
        
        try:
            while num:
                
                print(f"Papers {self.data.shape[0]} saved")
                elements = driver.find_elements(By.TAG_NAME, "li")
                articles = elements[:last_paper_on_page]
                next_page = self.url + f"/{page_num}"
                
                for article in articles:
                    
                    num -= 1
                    href = article.find_element(By.TAG_NAME, "a").get_attribute("href") 
                    driver.get(href)
                    
                    objects = driver.find_elements(By.TAG_NAME, "p")
                    
                    # get text of paper
                    text = ''
                    for obj in objects:
                        text += obj.text
                    
                    # author
                    try:
                        author = driver.find_element(By.CLASS_NAME, "hl").text
                    except:
                        author = None
                    try:
                        views = driver.find_element(By.CLASS_NAME, "statitem.views").text
                    except:
                        views = None
                    try:
                        down = driver.find_element(By.CLASS_NAME, "statitem.downloads").text
                    except:
                        down = None
                    try:
                        likes = driver.find_element(By.CLASS_NAME, "likes").text.split("\n")
                    except:
                        likes = [None, None]
                    try:
                        year = driver.find_element(By.CLASS_NAME, "label.year").find_element(By.TAG_NAME, "time").text
                    except:
                        year = None
                    try:    
                        journal = driver.find_element(By.CLASS_NAME, "half").find_elements(By.TAG_NAME, "a")[-1].text
                    except:
                        journal = None
                    try:
                        words = [i.text for i in driver.find_element(By.CLASS_NAME, "full.keywords").find_elements(By.CLASS_NAME, "hl.to-search")]
                    except:
                        words = None
                    try:
                        title = driver.find_element(By.TAG_NAME, "i").text
                    except:
                        title = None
                    
                    lst = [(href, 
                            author, 
                            title,
                            text, 
                            year, 
                            words, 
                            views, 
                            down, 
                            likes[0], 
                            likes[1], 
                            journal)]
                    to_add = pd.DataFrame(lst, columns=self.columns)
                    self.data = pd.concat([self.data, to_add], ignore_index=True)
                    sleep(10)
                    driver.back()
                
                # Change UA 
                driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua.random})
                driver.get(next_page)
                page_num += 1
                
        except Exception as ex:
            print("Last page:", page_num)
            traceback.print_exc()
            driver.quit()
            
        print("Last page:", page_num)
        return self.data
    
    def save(self):
        self.data.to_csv(self.path)
    