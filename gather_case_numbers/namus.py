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
import logging
import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logger = logging.getLogger()
logger.setLevel(LOGLEVEL)

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

def apply_filters(gt_date=None, lt_date=None, states=None):
    time.sleep(2)
    logger.debug("Adding filters")
    if states is not None: apply_state_filter(states)
    apply_date_filter(gt_date=gt_date, lt_date=lt_date)

def apply_date_filter(gt_date=None, lt_date=None):
    logger.debug('Setting date range...')
    if gt_date == None and lt_date == None:
        raise "must select a date"
    elif gt_date == None:
        date_operand = "<="
        operand_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[1]/select')
        Select(operand_box).select_by_visible_text(date_operand)

        month_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[1]/date-input/div/select[1]')
        Select(month_box).select_by_visible_text(lt_date.split('-')[0])

        day_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[1]/date-input/div/select[2]')
        Select(day_box).select_by_visible_text(lt_date.split('-')[1])

        year_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[1]/date-input/div/years-input/select')
        Select(year_box).select_by_visible_text(lt_date.split('-')[2])
    elif lt_date == None:
        date_operand = ">="
        operand_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[1]/select')
        Select(operand_box).select_by_visible_text(date_operand)

        month_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div/date-input/div/select[1]')
        Select(month_box).select_by_visible_text(gt_date.split('-')[0])

        day_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div/date-input/div/select[2]')
        Select(day_box).select_by_visible_text(gt_date.split('-')[1])

        year_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div/date-input/div/years-input/select')
        Select(year_box).select_by_visible_text(gt_date.split('-')[2])
    else:
        date_operand = "Between"
        operand_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[1]/select')
        Select(operand_box).select_by_visible_text(date_operand)

        month_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[1]/date-input/div/select[1]')
        Select(month_box).select_by_visible_text(gt_date.split('-')[0])

        day_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[1]/date-input/div/select[2]')
        Select(day_box).select_by_visible_text(gt_date.split('-')[1])

        year_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[1]/date-input/div/years-input/select')
        Select(year_box).select_by_visible_text(gt_date.split('-')[2])

        month_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[2]/date-input/div/select[1]')
        Select(month_box).select_by_visible_text(lt_date.split('-')[0])

        day_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[2]/date-input/div/select[2]')
        Select(day_box).select_by_visible_text(lt_date.split('-')[1])

        year_box = driver.find_element_by_xpath('//*[@id="Circumstances"]/div[3]/div/date-range-input/div/div[2]/div[1]/div[2]/date-input/div/years-input/select')
        Select(year_box).select_by_visible_text(lt_date.split('-')[2])



def apply_state_filter(states):
    logger.debug('Adding selected states to filter...')

    circumstances_section = driver.find_element_by_id('Circumstances')
    labels_in_section = circumstances_section.find_elements_by_tag_name('label')

    for label in labels_in_section:
        if (label.text == "State"):
            state_input_box = label.find_element_by_tag_name('input')
            for state in states:
                state_input_box.send_keys(state)
                state_input_box.send_keys(Keys.ENTER)
    
def get_page_numbers():
    logger.debug('Calculating number of pages...')
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_num_info = soup.find('nav', {'aria-label': 'Page Selection'}).find('span').text
    index_of_slash = re.search('/', page_num_info).span()[1]
    page_nums = int(page_num_info[index_of_slash:].strip())

    logger.debug(f'Calculated {page_nums} pages')
    return page_nums

def init_driver():
    logger.debug('Initializing global driver to variable named "driver"')
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')

    global driver
    driver = webdriver.Chrome('/opt/chromedriver', chrome_options=options)

def next_page():
    logger.debug('clicking next page...')

    try:
        driver.find_element_by_xpath("//i[@class=\"icon-triangle-right\"]").click()
        time.sleep(2)
    except:
        logger.info('last page completed...')

def process_data_on_page():
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
        
        logger.info("Collected data for case number:", message['caseNumber'])
        send_to_sqs(message)

def rows_to_show(num_rows):
    logger.debug(f'Setting {MAX_ROWS_PER_PAGE} rows per page...')

    time.sleep(2)
    results_selection_dropdown = driver.find_element_by_xpath('//*[@id="visitor"]/div[1]/div[4]/form/div[2]/section[2]/div/div/div/div/div[3]/div[3]/search-results-pager/ng-include/div/div/div/label/select')
    Select(results_selection_dropdown).select_by_value(f'{num_rows}')

def search():
    logger.debug('Searching...')
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

def main(gt_date=None, lt_date=None, states=None):
    init_driver()

    logger.debug('Navigating to namus.gov...')
    driver.get("https://www.namus.gov/MissingPersons/Search")

    apply_filters(gt_date=gt_date, lt_date=lt_date, states=states)
    search()
    rows_to_show(MAX_ROWS_PER_PAGE)
    page_nums = get_page_numbers()

    try:
        for page in range(page_nums):
            logger.debug(f'starting page {page}...')
            process_data_on_page()
            next_page()

        logger.debug('Scraping completed!')
        driver.quit()
    except Exception as e:
        logger.debug(f'Exception: {e}')
        driver.quit()
