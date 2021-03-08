from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pdb, time
import os
import logging

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

logger = logging.getLogger()
logger.setLevel(LOGLEVEL)

# CONSTANTS
SCRAPED_TO_DB_KEYS = {
    # Demographics Keys
    'Missing Age': 'missingAge',
    'Current Age': 'currentAge',
    'First Name': 'firstName',
    'Middle Name': 'middleName',
    'Last Name': 'lastName',
    'Nickname/Alias': 'nickname',
    'Sex': 'sex',
    'Height': 'height',
    'Weight': 'weight',
    'Race / Ethnicity': 'race',

    # Circumstance keys
    'Date of Last Contact': 'dateOfLastContact',
    'NamUs Case Created': 'namusCaseCreated',
    'Location': 'location',
    'County': 'county',
    'Circumstances of Disappearance': 'circumstancesOfDisappearance',

    # Physical Description Keys
    'Hair Color': 'hairColor',
    'Head Hair Description': 'headHairDescription',
    'Body Hair Description': 'bodyHairDescription',
    'Facial Hair Description': 'facialHairDescription',
    'Left Eye Color': 'leftEyeColor',
    'Right Eye Color': 'rightEyeColor',
    'Eye Description': 'eyeDescription',

    # Investigating Agency
    'Agency Name': 'agencyName',
    'Agency Investigator': 'agencyInvestigator',
    'Address': 'agencyAddress',
    'Agency County': 'agencyCounty',
    'Agency Type': 'agencyType',
    'Main Phone': 'agencyMainPhone',
    'General Email': 'agencyGeneralEmail',
    'Website URL': 'agencyWebsiteURL',
    'ORI': 'agencyOri',
    'Jurisdiction': 'agencyJurisdiction',
    'Agency Case Number': 'agencyCaseNumber',
    'Date Reported': 'agencyDateReported',
    'Notes': 'agencyNotes',

    # Contact Info
    'Namus Contact Name': 'namusContactName',
    'Namus Phone Number': 'namusPhoneNumber',
    'Namus Email': 'namusEmail'
}
KEYS_NOT_TO_MAP = [
    'Associated Tribe(s):',
    'Missing From Tribal Land',
    'Primary Residence on Tribal Land',
    'Item',
    'Description',
    'Phone',
    'Secondary Phone',
    'Email'
]

def scrape_demographics(record, driver):
    logger.debug('Scraping demographics section...')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    demographics_section = soup.find('div', id='Demographics')
    labels = demographics_section.find_all('span', class_='data-label')
    scraped_data = {}

    for label in labels:
        if (label.text.lower() != 'social security number'):
            scraped_data[label.text.strip()] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_circumstances(record, driver):
    logger.debug('Scraping circumstances section...')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    circumstances_section = soup.find('div', id='Circumstances')
    labels = circumstances_section.find_all('span', class_='data-label')
    scraped_data = {}

    for label in labels:
        if label.text.strip() == 'Location' or label.text.strip() == 'Circumstances of Disappearance':
            scraped_data[label.text.strip()] = label.next_sibling.next_sibling.text.strip()
        else:
            scraped_data[label.text.strip()] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_investigating_agencies(record, driver):
    logger.debug('Scraping investigating agencies section...')

    driver.find_element_by_id('InvestigatingAgencies').find_element_by_class_name('icon-chevron-down').click()
    wait_for_driver_load(By.CLASS_NAME, 'icon-chevron-up', driver, additional_sec=1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
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
    
    # change generic county key to specific agency county key and remove old key
    scraped_data['Agency County'] = scraped_data['County']
    scraped_data.pop('County', None) 
    
    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_namus_contact_section(record, driver):
    logger.debug('Scraping agencies contact section...')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    contact_info_section = soup.find('case-contact-information')
    scraped_data = {}

    scraped_data['Namus Contact Name'] = contact_info_section.find('span', class_='rsa-contact-name').text
    scraped_data['Namus Phone Number'] = contact_info_section.find('i', class_='icon-phone').next_sibling.strip() 
    scraped_data['Namus Email'] = contact_info_section.find('i', class_='icon-mail').next_sibling.strip() 

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_physical_description(record, driver):
    logger.debug('Scraping physical description section...')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    physical_description_section = soup.find('div', id='PhysicalDescription')
    data_labels = physical_description_section.find_all('span', class_='data-label')
    scraped_data = {}

    for label in data_labels:
        if label.text.strip() != 'Hair Color' and label.text.strip() != 'Item' and label.text.strip() != 'Description':
            scraped_data[label.text.strip()] = label.next_sibling.next_sibling.text.strip()
        else:
            scraped_data[label.text.strip()] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)
    
def map_scraped_keys_to_db_keys(scraped_data, record):
    for key in scraped_data:
        if key in KEYS_NOT_TO_MAP: continue
        record[SCRAPED_TO_DB_KEYS[key]] = scraped_data[key]

    return record

def wait_for_driver_load(by_identifier, identifier, driver, additional_sec=0):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by_identifier, identifier))
        )
        time.sleep(additional_sec)
    except Exception as e:
        logger.exception(f'Could not find {identifier} element after waiting 10 seconds.')
        raise e

def main(case_info, driver):
    case_id = case_info['caseNumber'][2:]

    logger.debug('Navigating to Namus.gov details section...')
    driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/details?nav')
    wait_for_driver_load(By.ID, 'Demographics', driver)
    case_info = scrape_demographics(case_info, driver)
    case_info = scrape_circumstances(case_info, driver)
    case_info = scrape_physical_description(case_info, driver)

    driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/contacts?nav')
    wait_for_driver_load(By.CLASS_NAME, 'rsa-contact', driver, additional_sec=0.5)
    case_info = scrape_namus_contact_section(case_info, driver)
    case_info = scrape_investigating_agencies(case_info, driver)

    return case_info
