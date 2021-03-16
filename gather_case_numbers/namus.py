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
import os
import logging
from os import path
import pandas as pd
from shutil import rmtree

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

logger = logging.getLogger()
logger.setLevel(LOGLEVEL)

# CONSTANTS
CASE_NUMBER_KEY = 'Case Number'
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
    'Race / Ethnicity': 'race',
    'Date Modified': 'dateModified'
}
DOWNLOAD_PATH = '/tmp/cases'

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

def download_csv():
    os.mkdir(DOWNLOAD_PATH)
    export_csv_link = '//*[@id="public"]/div[2]/div[4]/form/div[2]/section[2]/div/div/div/div/div[3]/div[2]/a/span'
    
    driver.find_element_by_xpath(export_csv_link).click()

    wait_time = 1
    while len(os.listdir(DOWNLOAD_PATH)) == 0:
        time.sleep(wait_time)
        if wait_time > 35:
            raise "Waited for {0} seconds and still could not find the download".format(wait_time)

        wait_time = wait_time * 2 # double the wait time every iteration
    
    downloaded_file_name = os.listdir(DOWNLOAD_PATH)[0]
    return path.join(DOWNLOAD_PATH, downloaded_file_name)

def init_driver():
    logger.debug('Initializing global driver to variable named "driver"')
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')

    prefs = {'download.default_directory' : DOWNLOAD_PATH}
    options.add_experimental_option('prefs', prefs)

    global driver
    driver = webdriver.Chrome('/opt/chromedriver', chrome_options=options)

def namus_login():
    login = '//*[@id="loginUsername"]'
    password_input = '//*[@id="loginPassword"]'
    login_button = '//*[@id="LoginSubmit"]'
    email = 'mism.traffick.stop@gmail.com'
    password = 'b5C4V68@*&2D'
    driver.find_element_by_xpath('//*[@id="visitor"]/div[2]/header/nav[2]/ul/li[3]/a').click()
    time.sleep(2)
    driver.find_element_by_xpath(login).send_keys(email)
    driver.find_element_by_xpath(password_input).send_keys(password)
    driver.find_element_by_xpath(login_button).click()
    time.sleep(5)

 def process_cases(file_name):
    df = pd.read_csv(file_name)
    df.rename(columns=SCRAPED_TO_DB_KEYS, inplace=True)

    for row in df.iterrows():
        send_to_sqs(row.to_dict())

def search():
    logger.debug('Searching...')
    search_results_section = driver.find_element_by_class_name('search-criteria-container')
    search_actions = search_results_section.find_element_by_class_name('search-criteria-container-actions').find_elements_by_tag_name('input')
    search_actions[1].click()
    time.sleep(1.5)

def send_to_sqs(record):
    logger.info("Sending to SQS for case number: {0}".format(record['caseNumber']))
    message = json.dumps(record)
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        MessageBody=message
    )
    logger.info("Successfully sent message for: {0}".format(record['caseNumber']))

def main(gt_date=None, lt_date=None, states=None):
    init_driver()

    print('Navigating to namus.gov...')
    driver.get("https://www.namus.gov/MissingPersons/Search")

    try:
        print('logging in to Namus account')
        namus_login()

        print('applying search filters')
        apply_filters(gt_date=gt_date, lt_date=lt_date, states=states)
        
        print('navigating to results')
        search()
        
        print('downloading csv')
        file_name = download_csv()

        print('sending cases to sqs')
        process_cases(file_name)

        print('removing temp directory and contents')
        rmtree(DOWNLOAD_PATH)

    except Exception as e:
        driver.quit()
        print(f'Exception: {e}')
        raise