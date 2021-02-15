from bs4 import BeautifulSoup
from helpers.selenium import SeleniumScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pdb

def init_driver():
    global driver
    driver = SeleniumScraper.get_driver()

    case_id = case_info['Case Number'][2:] # Case number format is "MP1234"
    driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/details?nav')

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Demographics'))
        )
    except Exception as e:
        print('Could not find initial element after waiting 10 seconds')
        raise e

def scrape_demographics(record):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    demographics_section = soup.find('div', id='Demographics')
    labels = demographics_section.find_all('span', class_='data-label')
    scraped_data = {}

    for label in labels:
        if (label.text.lower() != 'social security number'):
            scraped_data[label.text.strip()] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_circumstances(record):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    circumstances_section = soup.find('div', id='Circumstances')
    labels = circumstances_section.find_all('span', class_='data-label')
    scraped_data = {}

    for label in labels:
        if label.text.strip() == 'Location' or label.text.strip() == 'Circumstances of Disappearance':
            scraped_data[label.text.strip()] = label.next_sibling.next_sibling.text.strip()
        else:
            scraped_data[label.text.strip()] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_physical_description(record):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    physical_description_section = soup.find('div', id='PhysicalDescription')
    label_elements = physical_description_section.find_all('span', class_='data-label')
    scraped_data = {}

    for label in label_elements:
        if label.text.strip() != 'Hair Color' and label.text.strip() != 'Item' and label.text.strip() != 'Description':
            scraped_data[label.text.strip()] = label.next_sibling.next_sibling.text.strip()
        else:
            scraped_data[label.text.strip()] = label.next_sibling.strip()

    return map_scraped_keys_to_db_keys(scraped_data, record)
    
def map_scraped_keys_to_db_keys(scraped_data, record):
    # Demographics Keys
    record['Missing Age'] = scraped_data['Missing Age'] if 'Missing Age' in scraped_data else print('Error finding column Missing Age')
    record['Current Age'] = scraped_data['Current Age'] if 'Current Age' in scraped_data else print('Error finding column Current Age')
    record['First Name'] = scraped_data['First Name'] if 'First Name' in scraped_data else print('Error finding column First Name')
    record['Middle Name'] = scraped_data['Middle Name'] if 'Middle Name' in scraped_data else print('Error finding column Middle Name')
    record['Last Name'] = scraped_data['Last Name'] if 'Last Name' in scraped_data else print('Error finding column Last Name')
    record['Nickname'] = scraped_data['Nickname/Alias'] if 'Nickname/Alias' in scraped_data else print('Error finding column Nickname')
    record['Sex'] = scraped_data['Sex'] if 'Sex' in scraped_data else print('Error finding column Sex')
    record['Height'] = scraped_data['Height'] if 'Height' in scraped_data else print('Error finding column Height')
    record['Weight'] = scraped_data['Weight'] if 'Weight' in scraped_data else print('Error finding column Weight')
    record['Race'] = scraped_data['Race / Ethnicity'] if 'Race / Ethnicity' in scraped_data else print('Error finding column Race')

    # Circumstance keys
    record['Date of Last Contact'] = scraped_data['Date of Last Contact'] if 'Date of Last Contact' in scraped_data else print('Error finding column Date of Last Contact')
    record['NamUs Case Created'] = scraped_data['NamUs Case Created'] if 'NamUs Case Created' in scraped_data else print('Error finding column NamUs Case Created')
    record['Location'] = scraped_data['Location'] if 'Location' in scraped_data else print('Error finding column Location')
    record['County'] = scraped_data['County'] if 'County' in scraped_data else print('Error finding column County')
    record['Circumstances of Disappearance'] = scraped_data['Circumstances of Disappearance'] if 'Circumstances of Disappearance' in scraped_data else print('Error finding column Circumstances of Disappearance')

    # Physical Description Keys
    record['Hair Color'] = scraped_data['Hair Color'] if 'Hair Color' in scraped_data else print('Error finding column Hair Color')
    record['Head Hair Description'] = scraped_data['Head Hair Description'] if 'Head Hair Description' in scraped_data else print('Error finding column Head Hair Description')
    record['Body Hair Description'] = scraped_data['Body Hair Description'] if 'Body Hair Description' in scraped_data else print('Error finding column Body Hair Description')
    record['Facial Hair Description'] = scraped_data['Facial Hair Description'] if 'Facial Hair Description' in scraped_data else print('Error finding column Facial Hair Description')
    record['Left Eye Color'] = scraped_data['Left Eye Color'] if 'Left Eye Color' in scraped_data else print('Error finding column Left Eye Color')
    record['Right Eye Color'] = scraped_data['Right Eye Color'] if 'Right Eye Color' in scraped_data else print('Error finding column Right Eye Color')
    record['Eye Description'] = scraped_data['Eye Description'] if 'Eye Description' in scraped_data else print('Error finding column Eye Description')

    return record

def main(case_info):
    init_driver()
    case_info = scrape_demographics(case_info)
    case_info = scrape_circumstances(case_info)
    case_info = scrape_physical_description(case_info)

    return case_info
