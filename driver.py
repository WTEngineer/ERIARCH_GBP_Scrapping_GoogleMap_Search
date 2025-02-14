from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException, NoSuchElementException, ElementNotInteractableException
import threading
import time

class Driver:
    def __init__(self):
        self.createBrowser()
    
    def createBrowser(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1024,768")
        # self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        service = Service()
        # options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get('https://www.google.com/maps?hl=en')
        # if self.driver.find_element(By.XPATH, '//form[@action="https://consent.google.com/save"]'):
        #     self.driver.find_elements(By.XPATH, '//form[@action="https://consent.google.com/save"]')[1].click()
        self.status = 'ready'
        self.response = None

    def is_available(self):
        return self.status == 'ready'
    
    def reload_page(self):
        try:
            self.driver.get('https://www.google.com/maps?hl=en')
        except Exception:
            return

    def execute(self, task, url=None):
        try:
            if task == 'get_page' and url:
                # check if the element exist
                elements = self.driver.find_elements(By.XPATH, '//input[@id="searchboxinput"]')
                if len(elements) == 0:
                    # close
                    self.reload_page()
                else:
                    self.driver.find_element(By.XPATH, '//input[@id="searchboxinput"]').clear()
                    self.driver.find_element(By.XPATH, '//input[@id="searchboxinput"]').send_keys(url)
                    self.driver.find_element(By.XPATH, '//button[@id="searchbox-searchbutton"]').click()
                    time.sleep(4)
                    self.response = self.driver.page_source
            self.status = 'ready'
        except NoSuchElementException:
            # handle the exception
            print("Element not found")
            self.reload_page()
        except ElementNotInteractableException:
            self.reload_page()
        except InvalidSessionIdException:
            self.createBrowser()

    def get_page(self, url):
        self.status = 'busy'
        threading.Thread(target=self.execute, args=('get_page', url)).start()

    def has_response(self):
        return self.response is not None
    
    def get_response(self):
        if self.status == 'ready':
            result = self.response
            self.response = None
            return result
    
    def release(self):
        self.response = None
        self.status = 'ready'