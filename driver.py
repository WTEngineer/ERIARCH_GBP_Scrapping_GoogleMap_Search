from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import InvalidSessionIdException, NoSuchElementException, ElementNotInteractableException
import threading
import time
import random
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

driver_timeout = 1000

target_url = os.getenv("TARGET_URL")
# Path to your Chrome user profile
profile_path = os.getenv("CHROME_PROFILE_PATH")
profile_name = os.getenv("CHROME_PROFILE_NAME")

class Driver:
    def __init__(self):
        self.createBrowser()
    
    def createBrowser(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # Use the existing profile
        # chrome_options.add_argument(f"user-data-dir={profile_path}")  # Path to your user data folder
        # chrome_options.add_argument(f"profile-directory={profile_name}")  # You can specify the profile name, e.g., Default
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevents WebDriver detection
        chrome_options.add_argument("--window-size=1280,800")
        # self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Loading Page ...")
        self.driver.get(target_url)
        print("--------Ready------")
        self.status = 'ready'
        self.response = None

    def is_available(self):
        return self.status == 'ready'
    
    def reload_page(self):
        try:
            self.driver.get(target_url)
        except Exception:
            return
        
    # get category page 
    def get_google_search_execute(self, search_query, page_name):
        try:
            WebDriverWait(self.driver, driver_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@name="q"]')))
            # Locate the search box using its name attribute value
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.clear()
            # Type the search query
            search_box.send_keys(search_query)
            # Press Enter
            search_box.send_keys(Keys.RETURN)
            # wait to see title from google search
            WebDriverWait(self.driver, driver_timeout).until(EC.presence_of_element_located((By.XPATH, '//div[@id="w7tRq"]')))
            # WebDriverWait(self.driver, driver_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@data-attrid="title"]')))
            # Wait for a few seconds to see the results
            time.sleep(random.uniform(3, 5))
            self.response = self.driver.page_source
            self.status = 'ready'
        except Exception as err:
            print("Exception in get shazam charts")
            print(err)

    def get_google_search(self, search_word):
        self.status = 'busy'
        threading.Thread(target=self.get_google_search_execute, args=(search_word, "get_category_search")).start()

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
                    time.sleep(random.uniform(3, 5))
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

    def close(self):
        self.release()
        self.driver.close()