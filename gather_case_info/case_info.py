from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pdb

SCRAPED_TO_DB_KEYS = {
    # Demographics Keys
    'Missing Age': 'Missing Age',
    'Current Age': 'Current Age',
    'First Name': 'First Name',
    'Middle Name': 'Middle Name',
    'Last Name': 'Last Name',
    'Nickname/Alias': 'Nickname',
    'Sex': 'Sex',
    'Height': 'Height',
    'Weight': 'Weight',
    'Race / Ethnicity': 'Race',

    # Circumstance keys
    'Date of Last Contact': 'Date of Last Contact',
    'NamUs Case Created': 'NamUs Case Created',
    'Location': 'Location',
    'County': 'County',
    'Circumstances of Disappearance': 'Circumstances of Disappearance',

    # Physical Description Keys
    'Hair Color': 'Hair Color',
    'Head Hair Description': 'Head Hair Description',
    'Body Hair Description': 'Body Hair Description',
    'Facial Hair Description': 'Facial Hair Description',
    'Left Eye Color': 'Left Eye Color',
    'Right Eye Color': 'Right Eye Color',
    'Eye Description': 'Eye Description',

    # Investigating Agency
    'Agency Name': 'Agency Name',
    'Agency Investigator': 'Agency Investigator',
    'Address': 'Agency Address',
    'County': 'Agency County',
    'Agency Type': 'Agency Type',
    'Main Phone': 'Agency Main Phone',
    'General Email': 'Agency General Email',
    'Website URL': 'Agency Website URL',
    'ORI': 'Agency ORI',
    'Jurisdiction': 'Agency Jurisdiction',
    'Agency Case Number': 'Agency Case Number',
    'Date Reported': 'Agency Date Reported',
    'Notes': 'Agency Notes',

    # Contact Info
    'Namus Contact Name': 'Namus Contact Name',
    'Namus Phone Number': 'Namus Phone Number',
    'Namus Email': 'Namus Email'
}

def init_driver():
    config = ['ignore-certificate-errors', 'incognito', 'headless']
    options = webdriver.ChromeOptions()
    for option in config:
        options.add_argument(f'--{option}')

    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    wait_for_driver_load(By.ID, 'Demographics')

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
    soup = BeautifulSoup(driver.page_source, 'lxml')
    contact_info_section = soup.find('case-contact-information')
    scraped_data = {}

    scraped_data['Namus Contact Name'] = contact_info_section.find('span', class_='rsa-contact-name').text
    scraped_data['Namus Phone Number'] = contact_info_section.find('i', class_='icon-phone').next_sibling.strip() 
    scraped_data['Namus Email'] = contact_info_section.find('i', class_='icon-mail').next_sibling.strip() 

    return map_scraped_keys_to_db_keys(scraped_data, record)

def scrape_physical_description(record):
    soup = BeautifulSoup(driver.page_source, 'lxml')
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
        record[SCRAPED_TO_DB_KEYS[key]] = scraped_data[key]

    return record

def wait_for_driver_load(by_identifier, identifier, additional_sec=0):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by_identifier, identifier))
        )
        time.sleep(additional_sec)
    except Exception as e:
        print(f'Could not find {identifier} element after waiting 10 seconds.')
        raise e

def main(case_info):
    init_driver()
    case_id = case_info['Case Number'][2:] # Case number format is "MP1234"

    driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/details?nav')
    wait_for_driver_load(By.ID, 'Demographics')
    case_info = scrape_demographics(case_info)
    case_info = scrape_circumstances(case_info)
    case_info = scrape_physical_description(case_info)

    driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/contacts?nav')
    wait_for_driver_load(By.CLASS_NAME, 'rsa-contact', additional_sec=0.5)
    case_info = scrape_namus_contact_section(case_info)
    case_info = scrape_investigating_agencies(case_info)

    return case_info
