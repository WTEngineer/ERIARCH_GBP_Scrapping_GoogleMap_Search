from driver import Driver
from bs4 import BeautifulSoup
import csv, time
from rich import print
import random
import datetime
import time
from dotenv import load_dotenv
import os
import requests
import re
import datetime
import sys
import csv

load_dotenv()  # Load environment variables from .env file

WAIT_TIME_LIMIT = 1000

class Scraper:
    def __init__(self):
        self.DriversPool = []
        # in case of one-time mode
        self.DriversSize = 1
        self.DriversPool = [Driver() for _ in range(self.DriversSize)]
    
    def closeDrivers(self):
        for driver in self.DriversPool:
            driver.close()

    def searchGoogle(self, search_word, random_id):
        while True:
            try:
                for driver in self.DriversPool:
                    if driver.is_available() and not driver.has_response():
                        driver.get_google_search(search_word)
                        break
                else:
                    time.sleep(2)
                    print(f'[{random_id}] Waiting for a driver to be available...')
                    continue
                break
            except Exception as err:
                print(err)

        wait_time = 0
        while True:
            try:
                if driver.has_response():
                    break
                time.sleep(1)
                print(f'[{random_id}] Waiting for a response...')
                wait_time += 1
                if wait_time == WAIT_TIME_LIMIT: 
                    driver.release()
                    return
            except Exception as err:
                print(err)
                return None

        soup = BeautifulSoup(driver.get_response(), 'html.parser')
        # Initialize variables to hold extracted info
        category = ""
        price_range = ""
        facility_description = ""
        service_options = ""
        
        # Extract price range (if available) G
        subtitle_div = soup.find("div", attrs={"data-attrid": "subtitle"})
        if subtitle_div:
            price_range_element = subtitle_div.find_all("span")[-3]
            if price_range_element:
                price_range = price_range_element.text.strip()

        # Extract category (handle different category element classes) D
        category_element = soup.find("span", class_=re.compile("E5BaQ|YhemCb"))
        if category_element:
            category = category_element.text.strip()
        
        # Extract Facility Description H
        # Look for the facility description
        facility_desc_element = soup.find('span', {'class': 'Yy0acb'})  
        if facility_desc_element:
            facility_description = facility_desc_element.text.strip()
        # Try Extract Summary
        summary = None
        summary_element = soup.find('div', {'class': 'kno-rdesc'})
        if summary_element:
            summary_child_tags = summary_element.findChildren('span')
            summary = summary_child_tags[0].text.strip() if summary_child_tags else None
        if summary:
            facility_description = f"{facility_description} {summary}".strip()
        highlights = None
        highlights_element = soup.find('span', {'class': 'vTmgGc'})
        if highlights_element:
            highlights = highlights_element.text.strip()
        if highlights:
            facility_description = f"{facility_description} {highlights}".strip()

        # Extract Service Options (related tag2) I
        service_options_tag = soup.find('span', {'class': 'GKdNbc'}) 
        if service_options_tag:
            service_options_element = service_options_tag.find_next_sibling('span')
            if service_options_element:
                service_options = service_options_element.text.strip()

        driver.release()
        
        # Return the extracted data
        return {
            'price_range': price_range,
            'category': category,
            'facility_description': facility_description,
            'service_options': service_options
        }

    def startProc(self, search_word):
        res = self.searchGoogle(search_word, random.randint(10000, 99999))
        print(res)
        time.sleep(2)
        self.closeDrivers()


if __name__ == '__main__':

    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d %H-%M-%S")

    print("Usage: python test.py <search word>")
    search_word = sys.argv[1] if len(sys.argv) > 1 else None

    while True:

        if search_word is None:
            search_word = input("Search Word: ")

        if search_word is None or search_word.strip() == "":
            print(f"Search Word is required!")
            search_word = None
            continue

        break

    print("======== Starting the App ==========")

    obj = Scraper()
    obj.startProc(search_word)

