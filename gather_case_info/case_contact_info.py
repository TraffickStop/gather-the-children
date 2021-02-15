from bs4 import BeautifulSoup
from helpers.selenium import SeleniumScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import pdb, time

# CONSTANTS
SCRAPED_TO_DB_KEYS = {
    'Case Number',
    'Namus Contact Name',
    'Namus Phone Number',
    'Namus Email',
    'Agency Name',
    'Agency Address',
    'Agency County',
    'Agency Type',
    'Agency Main Phone',
    'Agency General Email',
    'Agency Website URL',
    'Agency ORI',
    'Agency Jurisdiction',
    'Agency Case Number',
    'Agency Date Reported',
    'Agency Notes',
    'Agency Investigator'
}

def init_driver():
    global driver
    driver = SeleniumScraper.get_driver()

    case_id = case_info['Case Number'][2:] # Case number format is "MP1234"
    driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/contacts?nav')

def map_scraped_keys_to_db_keys(scraped_data, record):
    # Investigating Agency
    record['Agency Name'] = agency_name
    record['Agency Address'] = scraped_data['Address'] if 'Address' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency County'] = scraped_data['County'] if 'County' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Type'] = scraped_data['Agency Type'] if 'Agency Type' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Main Phone'] = scraped_data['Main Phone'] if 'Main Phone' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency General Email'] = scraped_data['General Email'] if 'General Email' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Website URL'] = scraped_data['Website URL'] if 'Website URL' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency ORI'] = scraped_data['ORI'] if 'ORI' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Jurisdiction'] = scraped_data['Jurisdiction'] if 'Jurisdiction' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Case Number'] = scraped_data['Agency Case Number'] if 'Agency Case Number' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Date Reported'] = scraped_data['Date Reported'] if 'Date Reported' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Notes'] = scraped_data['Notes'] if 'Notes' in scraped_data else print(f'Error finding column for {case_number}')
    record['Agency Investigator'] = agency_investigator

    return record

def scrape_investigating_agencies(record):
    driver.find_element_by_id('InvestigatingAgencies').find_element_by_class_name('icon-chevron-down').click()
    wait_for_driver_load(By.CLASS_NAME, 'icon-chevron-up', additional_sec=1)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    investigating_agencies_section = soup.find('div', id='InvestigatingAgencies')
    scraped_data = {}

    scraped_data['Agency Name'] = investigating_agencies_section.find('i', class_='icon-chevron-up').find_next_sibling('span', class_='name-inline').text

    if len(investigating_agencies_section.find('case-contact').find_all('h4')) > 0:
        scraped_data['Agency Investigator'] = investigating_agencies_section.find('case-contact').find_all('h4')[0].text.strip()
    else:
        scraped_data['Agency Investigator'] = None

    data_labels = investigating_agencies_section.find_all('span', class_='data-label')
    for label in data_labels:
        if label.text.lower() == 'address':
            scraped_data['Address'] = label.find_next_sibling('span', class_='multi-line').text
        else:
            scraped_data[label.text] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_namus_contact_section(record):
    wait_for_driver_load(By.CLASS_NAME, 'rsa-contact', additional_sec=0.5)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    contact_info_section = soup.find('case-contact-information')
    scraped_data = {}

    scraped_data['Namus Contact Name'] = contact_info_section.find('span', class_='rsa-contact-name').text
    scraped_data['Namus Phone Number'] = contact_info_section.find('i', class_='icon-phone').next_sibling.strip() 
    scraped_data['Namus Email'] = contact_info_section.find('i', class_='icon-mail').next_sibling.strip() 

    return map_scraped_keys_to_db_keys(scraped_data, record)

def wait_for_driver_load(by_identifier, identifier, additional_sec=0):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by_identifier, identifier))
        )
        time.sleep(additional_sec)
    except Exception as e:
        print('could not find element after waiting 10 seconds.')
        raise e

def main(case_info):
    init_driver()
    case_info = scrape_namus_contact_section(case_info)
    case_info = scrape_investigating_agencies(case_info)

    return case_info
