from selenium import webdriver
import time


class VerCodeRec:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.url = 'https://aq.qq.com/cn2/login_limit/login_limit_index'

    def open_web(self):
        try:
            self.driver.get(self.url)
            self.web_setting(self.scheduler_by_url())
        except:
            time.sleep(10)
            self.open_web()