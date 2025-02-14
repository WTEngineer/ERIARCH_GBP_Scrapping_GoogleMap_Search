from driver import Driver
from bs4 import BeautifulSoup
import csv, time
from rich import print
import concurrent.futures
import random
import traceback

def find_business(row, random_id):
    while True:
        try:
            for driver in DriversPool:
                if driver.is_available() and not driver.has_response():
                    driver.get_page(row['address'])
                    break
            else:
                time.sleep(1)
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
            # print(f'[{random_id}] Waiting for a response...')
            wait_time += 1
            if wait_time == 15: 
                driver.release()
                return
        except Exception as err:
            print(err)
            return
        
    soup = BeautifulSoup(driver.get_response(), 'html.parser')

    info = {}

    if not soup.find('h1') or not soup.find('button', {'data-item-id': 'address'}): 
        driver.release()
        info['name'] = 'Not Found'
        row.update(info)
        return row

    info['name']     = soup.find('h1').text
    info['gaddress']  = soup.find('button', {'data-item-id': 'address'})['aria-label'].split(': ')[-1] if soup.find('button', {'data-item-id': 'address'}) else None
    info['website']  = soup.find('a', {'data-item-id': 'authority'})['href'] if soup.find('a', {'data-item-id': 'authority'}) else None
    info['phone']    = soup.find('button', {'data-tooltip': 'Copy phone number'})['aria-label'].split(': ')[-1] if soup.find('button', {'data-tooltip': 'Copy phone number'}) else None
    info['category'] = soup.find('button', {'jsaction': 'pane.rating.category'}).text if soup.find('button', {'jsaction': 'pane.rating.category'}) else None

    row.update(info)
    driver.release()
    return row

if __name__ == '__main__':
    for file_id in range(9, 87):
        input_file = open(f'input/Data/data{file_id}.csv', 'r', encoding='utf-8')
        output_file = open(f'output/output{file_id}.csv', 'a+', newline='', encoding='utf8')
        # input_file = open('input.csv', 'r', encoding='utf-8')
        # output_file = open('output.csv', 'a+', newline='', encoding='utf8')
        reader = csv.reader(input_file)
        DriversSize = 1
        DriversPool = [Driver() for _ in range(DriversSize)]
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=DriversSize)
        writer = csv.writer(output_file)
        # writer.writeheader()
        futures = []
        count = 0
        for row in reader:
            address     = row[1]
            description = row[2]
            count += 1
            initial_row = {'address': address, 'description': description}
            futures.append(executor.submit(find_business, initial_row, random.randint(10000, 99999)))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                row = future.result()
                if (row is None):
                    continue
                writer.writerow(row.values())
                output_file.flush()
                print(row)
            except Exception as err:
                traceback.print_exc()
        executor.shutdown(wait=True)