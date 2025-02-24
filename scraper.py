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

WAIT_TIME_LIMIT = 1000  #Limit time

class Scraper:
    def __init__(self):
        self.DriversPool = []
        # in case of one-time mode
        self.DriversSize = 1
        self.DriversPool = [Driver() for _ in range(self.DriversSize)]
        self.searchKey = "検索キーワード"
    
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
            br_element = subtitle_div.find("br")
            if br_element:
                price_range_element = br_element.find_next_sibling('span')
                # Check if the next sibling is a <span> containing price range
                if price_range_element and price_range_element.get('class')  == None and price_range_element.find('span'):
                    price_range = price_range_element.find('span').get_text(strip=True)

        # Extract category (handle different category element classes) D
        category_element = soup.find("span", class_=re.compile("E5BaQ|YhemCb"))
        if category_element:
            category = category_element.text.strip()
        
        # Extract Facility Description H
        #@ Look for the facility description
        facility_desc_element = soup.find('span', {'class': 'Yy0acb'})  
        if facility_desc_element:
            facility_description = facility_desc_element.text.strip()
        #@ Try Extract Summary
        summary = None
        summary_element = soup.find('div', {'class': 'kno-rdesc'})
        if summary_element:
            summary_child_tags = summary_element.findChildren('span')
            summary = summary_child_tags[0].text.strip() if summary_child_tags else None
        if summary:
            facility_description = f"{facility_description} {summary}".strip()
        ## Extract Highlights
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

    def writeSearchResult(self, csvPath):

        # Get the current date and time
        current_time = datetime.datetime.now()
        # Format the timestamp for the file name
        formatted_time = current_time.strftime('%Y-%m-%d_%H-%M')

        output_folder = "output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # print(f"{csvPath}")

        # Extract the filename for output naming
        csvFileName = os.path.basename(csvPath)

        with open(f"{csvPath}", "r", encoding="utf-8") as file:
            # reader = csv.reader(file)
            reader = csv.DictReader(file)  # Read rows as dictionaries
            if reader.fieldnames is None:
                print("Error: CSV file is missing headers or is empty.")
                return

            output_file_path = os.path.join(output_folder, f'出力_{formatted_time}_{csvFileName}')

            with open(output_file_path, 'w+', newline='', encoding='utf-8-sig') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)
                writer.writeheader()
                output_file.flush()

                for index, row in enumerate(reader):
                    search_word = row.get(self.searchKey, "")
                    print(f"-------- Run Google Searching: `{search_word}` --------")
                    res = self.searchGoogle(search_word, random.randint(10000, 99999))
                    row["注目のキーワード"] = res["category"]       # D
                    row['関連tag2（サービスオプション）'] = res["service_options"]     # F
                    row['価格帯'] = res["price_range"]           # G
                    row["place_overview"] = res["facility_description"]           # H
                    print(row, index + 1)
                    writer.writerow(row)
                    output_file.flush()  # Ensure immediate writing

    def startProc(self, csvPath):
        self.writeSearchResult(csvPath)
        time.sleep(2)
        self.closeDrivers()


if __name__ == '__main__':

    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d %H-%M-%S")

    print("Usage: python scraper.py <csv path>")
    csvPath = sys.argv[1] if len(sys.argv) > 1 else None

    while True:

        if csvPath is None:
            csvPath = input("CSV Path: ")

        if csvPath is None or csvPath.strip() == "":
            print(f"CSV Path is required!")
            csvPath = None
            continue

        break

    print("======== Starting the App ==========")

    obj = Scraper()
    obj.startProc(csvPath)


