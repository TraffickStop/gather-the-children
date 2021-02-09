from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import pdb, time

# CONSTANTS
MISSING_PERSONS_FILE = './data_files/All-Missing-People.infer'
CONTACT_COLUMNS = [
    'Case Number',
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
    'Agency Date Reported',
    'Agency Investigator'
]

# global variables
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def scrape_investigating_agencies(new_df):
    row = new_df.iloc[0]
    case_number = row['Case Number'] 

    driver.find_element_by_id('InvestigatingAgencies').find_element_by_class_name('icon-chevron-down').click()

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'icon-chevron-up'))
        )
        time.sleep(0.5)
    except Exception as e:
        print('could not find element')
        raise e

    soup = BeautifulSoup(driver.page_source, 'lxml')
    investigating_agencies_section = soup.find('div', id='InvestigatingAgencies')

    agency_name = investigating_agencies_section.find('i', class_='icon-chevron-up').find_next_sibling('span', class_='name-inline').text

    if len(investigating_agencies_section.find('case-contact').find_all('h4')) > 0:
        agency_investigator = investigating_agencies_section.find('case-contact').find_all('h4')[0].text.strip()
    else:
        agency_investigator = None

    dataframe_labels = {}

    # TODO: get all data-labels for some reason it's cutting off Agency Case Number and date reported as well as notes
    data_labels = investigating_agencies_section.find('div', class_='contact-expanded').find_all('span', class_='data-label')
    for label in data_labels:
        if label.text.lower() == 'address':
            dataframe_labels['Address'] = label.find_next_sibling('span', class_='multi-line').text
        else:
            pdb.set_trace()
            dataframe_labels[label.text] = label.next_sibling.strip()
   pdb.set_trace() 
    row['Agency Name'] = agency_name
    row['Agency Address'] = dataframe_labels['Address'] if 'Address' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency County'] = dataframe_labels['County'] if 'County' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency Type'] = dataframe_labels['Agency Type'] if 'Agency Type' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency Main Phone'] = dataframe_labels['Main Phone'] if 'Main Phone' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency General Email'] = dataframe_labels['General Email'] if 'General Email' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency Website URL'] = dataframe_labels['Website URL'] if 'Website URL' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency ORI'] = dataframe_labels['ORI'] if 'ORI' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency Date Reported'] = dataframe_labels['Jurisdiction'] if 'Jurisdiction' in dataframe_labels else print(f'Error finding column for {case_number}')
    row['Agency Investigator'] = agency_investigator

    return row

def scrape_namus_contact_section(row):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'rsa-contact'))
        )
        time.sleep(0.5)
    except Exception as e:
        print('could not find element')
        raise e

    soup = BeautifulSoup(driver.page_source, 'lxml')
    contact_info_section = soup.find('case-contact-information')

    namus_contact_name = contact_info_section.find('span', class_='rsa-contact-name').text
    namus_contact_phone = contact_info_section.find('i', class_='icon-phone').next_sibling.strip() 
    namus_contact_email = contact_info_section.find('i', class_='icon-mail').next_sibling.strip() 

    row['Namus Contact Name'] = namus_contact_name
    row['Namus Phone Number'] = namus_contact_phone
    row['Namus Email'] = namus_contact_email

    return row

def main():
    all_cases = pd.read_pickle(MISSING_PERSONS_FILE)
    case_contacts = pd.DataFrame(columns=CONTACT_COLUMNS)
    path = f'./data_files/case_contact_info{time.time()}.infer'

    for index, row in all_cases.iterrows():
        if index % 5 == 0: pdb.set_trace() # save 100 results to out file
        try:
            print(index)
            case_id = row['Case Number'][2:] # Case number format is "MP1234"

            case_contact_row = pd.DataFrame(columns=CONTACT_COLUMNS).append(pd.Series(dtype="object"), ignore_index=True)
            case_contact_row.iloc[0]['Case Number'] = row['Case Number']

            driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/contacts?nav')

            case_contact_row = scrape_namus_contact_section(case_contact_row)
            case_contact_row = scrape_investigating_agencies(case_contact_row)

            case_contacts = case_contacts.append(case_contact_row, ignore_index=True)
        except Exception as e:
            print(e)
            print(index, row)
            pdb.set_trace()
            case_contacts.to_pickle(path)
    
    pdb.set_trace()
    case_contacts.to_pickle(path)

if __name__ == '__main__':
    main()
