from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import pdb

# CONSTANTS
MISSING_PERSONS_FILE = './data_files/All-Missing-People.infer'
CONTACT_COLUMNS = [
    'Namus Contact Name',
    'Namus Phone Number',
    'Namus Email',
    'Agency Name',
    'Agency Address',
    'Agency County',
    'Agency Email',
    'Agency Website',
    'Agency ORI',
    'Agency Jurisdiction',
    'Agency Case Number',
    'Agency Date Reported'
]

# global variables
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def scrape_case_contributors(row):
    soup = BeautifulSoup(driver.page_source, 'lxml')

def scrape_investigating_agencies(row):
    driver.find_element_by_id('InvestigatingAgencies').find_element_by_class_name('icon-chevron-down').click()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    investigating_agencies_section = soup.find('div', id='InvestigatingAgencies')

    agency_name = investigating_agencies_section.find('i', class_='icon-chevron-up').find_next_sibling('span', class_='name-inline').text
    labels = {}

    data_labels = investigating_agencies_section.find('div', class_='contact-expanded').find_all('span', class_='data-label')
    for label in data_labels:
        if label.text.lower() == 'address':
            labels['Address'] = label.find_next_sibling('span', class_='multi-line').text
        else:
            labels[label.text] = label.next_sibling.strip()
    
    return row

def scrape_namus_contact_section(row):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    contact_info_section = soup.find('case-contact-information')
    namus_contact_name = contact_info_section.find('span', class_='rsa-contact-name').text
    namus_contact_phone = contact_info_section.find('i', class_='icon-phone').next_sibling.strip() 
    namus_contact_email = contact_info_section.find('i', class_='icon-mail').next_sibling.strip() 

    pdb.set_trace()
    return row

def main():
    all_cases = pd.read_pickle(MISSING_PERSONS_FILE)
    case_contacts = pd.DataFrame(columns=CONTACT_COLUMNS)

    for index, row in all_cases.iterrows():
        print(index)
        pdb.set_trace()
        new_row = pd.DataFrame(columns=CONTACT_COLUMNS)

        case_id = row['Case Number'][2:]
        driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/contacts?nav')

        new_row = scrape_namus_contact_section(new_row)
        new_row = scrape_investigating_agencies(new_row)
        new_row = scrape_case_contributors(new_row)

        case_contacts = case_contacts.append(new_row, ignore_index=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        pdb.set_trace()