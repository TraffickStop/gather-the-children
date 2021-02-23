import boto3
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pdb, re, time

# CONSTANTS
CASE_NUMBER_KEY = 'Case Number'
INFO_COLUMNS = [
    'Case Number',
    'DLC',
    'Last Name',
    'First Name',
    'Missing Age',
    'City',
    'County',
    'State',
    'Sex',
    'Race',
    'Date Modified'
]
SCRAPED_TO_DB_KEYS = {
    'Case Number': 'caseNumber',
    'DLC': 'dlc',
    'Last Name': 'lastName',
    'First Name': 'firstName',
    'Missing Age': 'missingAge',
    'City': 'city',
    'County': 'county',
    'State': 'state',
    'Sex': 'sex',
    'Race': 'race',
    'Date Modified': 'dateModified'
}
MAX_ROWS_PER_PAGE = 100

def apply_filters(last_date, date_operand, states):
    if states is not None: apply_state_filter(states)
    apply_date_filter(last_date, date_operand)

def apply_date_filter(date, date_operand):
    print('Adding date filters...')
    month = date.split('-')[0]
    day = date.split('-')[1]
    year = date.split('-')[2]

    circumstances_section = driver.find_element_by_id('Circumstances')
    operand_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[0]
    Select(operand_box).select_by_visible_text(date_operand)

    time.sleep(.5)

    month_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[1]
    Select(month_box).select_by_visible_text(month)

    day_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[2]
    Select(day_box).select_by_visible_text(day)

    year_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[3]
    Select(year_box).select_by_visible_text(year)

def apply_state_filter(states):
    print('Adding selected states to filter...')

    circumstances_section = driver.find_element_by_id('Circumstances')
    labels_in_section = circumstances_section.find_elements_by_tag_name('label')

    for label in labels_in_section:
        if (label.text == "State"):
            state_input_box = label.find_element_by_tag_name('input')
            for state in states:
                state_input_box.send_keys(state)
                state_input_box.send_keys(Keys.ENTER)
    
def get_page_numbers():
    print('Calculating number of pages...')
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_num_info = soup.find('nav', {'aria-label': 'Page Selection'}).find('span').text
    index_of_slash = re.search('/', page_num_info).span()[1]
    page_nums = int(page_num_info[index_of_slash:].strip())

    return page_nums

def init_driver():
    print('Initializing global driver to variable named "driver"')
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    global driver
    driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)

def next_page():
    print('clicking next page...')
    time.sleep(5)

    try:
        driver.find_element_by_xpath("//i[@class=\"icon-triangle-right\"]").click()
    except:
        print('last page completed...')

def process_data_on_page():
    print('Gathering info...')

    # navigate to list view
    driver.find_element_by_xpath("//i[@class=\"icon-list\"]").click()
    time.sleep(1.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find('div', class_='ui-grid-canvas').contents

    for row in rows:
        if row == ' ': continue

        case_info = {}
        cells = row.find_all('div', class_='ui-grid-cell-contents')
        for index, cell in enumerate(cells):
            case_info[INFO_COLUMNS[index]] = cell.text.strip()
        
        message = {}
        for key in case_info:
            message[SCRAPED_TO_DB_KEYS[key]] = case_info[key]
            
        send_to_sqs(message)
        break

def rows_to_show(num_rows):
    print(f'Setting {MAX_ROWS_PER_PAGE} rows per page...')

    results_selection_dropdown = driver.find_element_by_xpath("//label/span[contains(text(),'Results')]/following-sibling::select")
    Select(results_selection_dropdown).select_by_value(f'{num_rows}')
    time.sleep(1.5)

def search():
    print('Searching...')
    search_results_section = driver.find_element_by_class_name('search-criteria-container')
    search_actions = search_results_section.find_element_by_class_name('search-criteria-container-actions').find_elements_by_tag_name('input')
    search_actions[1].click()
    time.sleep(1.5)

def send_to_sqs(record):
    message = json.dumps(record)
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        MessageBody=message
    )

def main(last_date, date_operand=">=", states=None):
    init_driver()

    print('Navigating to namus.gov...')
    driver.get("https://www.namus.gov/MissingPersons/Search")

    apply_filters(last_date, date_operand, states)
    search()
    rows_to_show(MAX_ROWS_PER_PAGE)
    page_nums = get_page_numbers()

    try:
        for page in range(page_nums):
            print(f'starting page {page}...')
            process_data_on_page()
            return
            next_page()

        print('Scraping completed!')
        driver.quit()
    except Exception as e:
        print(f'Exception: {e}')
        driver.quit()
