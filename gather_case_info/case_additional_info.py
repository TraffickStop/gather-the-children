from bs4 import BeautifulSoup
from helpers.selenium import SeleniumScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import pdb, time

# CONSTANTS
MISSING_PERSONS_FILE = './data_files/All-Missing-People.infer'
ADDITIONAL_INFO_COLUMNS = [
    'Case Number',
    'Missing Age',
    'Current Age',
    'First Name',
    'Middle Name',
    'Last Name',
    'Nickname',
    'Sex',
    'Height',
    'Weight',
    'Race',
    'Date of Last Contact',
    'NamUs Case Created',
    'Location',
    'County',
    'Circumstances of Disappearance',
    'Hair Color',
    'Head Hair Description',
    'Body Hair Description',
    'Facial Hair Description',
    'Left Eye Color',
    'Right Eye Color',
    'Eye Description'
]

def scrape_demographics(row):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    demographics_section = soup.find('div', id='Demographics')
    labels = demographics_section.find_all('span', class_='data-label')

    row_labels = {}

    for label in labels:
        if (label.text.lower() != 'social security number'):
            row_labels[label.text.strip()] = label.next_sibling.strip()

    row['Missing Age'] = row_labels['Missing Age'] if 'Missing Age' in row_labels else print('Error finding column Missing Age')
    row['Current Age'] = row_labels['Current Age'] if 'Current Age' in row_labels else print('Error finding column Current Age')
    row['First Name'] = row_labels['First Name'] if 'First Name' in row_labels else print('Error finding column First Name')
    row['Middle Name'] = row_labels['Middle Name'] if 'Middle Name' in row_labels else print('Error finding column Middle Name')
    row['Last Name'] = row_labels['Last Name'] if 'Last Name' in row_labels else print('Error finding column Last Name')
    row['Nickname'] = row_labels['Nickname/Alias'] if 'Nickname/Alias' in row_labels else print('Error finding column Nickname')
    row['Sex'] = row_labels['Sex'] if 'Sex' in row_labels else print('Error finding column Sex')
    row['Height'] = row_labels['Height'] if 'Height' in row_labels else print('Error finding column Height')
    row['Weight'] = row_labels['Weight'] if 'Weight' in row_labels else print('Error finding column Weight')
    row['Race'] = row_labels['Race / Ethnicity'] if 'Race / Ethnicity' in row_labels else print('Error finding column Race')

    return row

def scrape_circumstances(row):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    circumstances_section = soup.find('div', id='Circumstances')
    labels = circumstances_section.find_all('span', class_='data-label')
    
    row_labels = {}

    for label in labels:
        if label.text.strip() == 'Location' or label.text.strip() == 'Circumstances of Disappearance':
            row_labels[label.text.strip()] = label.next_sibling.next_sibling.text.strip()
        else:
            row_labels[label.text.strip()] = label.next_sibling.strip()
    
    row['Date of Last Contact'] = row_labels['Date of Last Contact'] if 'Date of Last Contact' in row_labels else print('Error finding column Date of Last Contact')
    row['NamUs Case Created'] = row_labels['NamUs Case Created'] if 'NamUs Case Created' in row_labels else print('Error finding column NamUs Case Created')
    row['Location'] = row_labels['Location'] if 'Location' in row_labels else print('Error finding column Location')
    row['County'] = row_labels['County'] if 'County' in row_labels else print('Error finding column County')
    row['Circumstances of Disappearance'] = row_labels['Circumstances of Disappearance'] if 'Circumstances of Disappearance' in row_labels else print('Error finding column Circumstances of Disappearance')

    return row

def scrape_physical_description(row):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    physical_description_section = soup.find('div', id='PhysicalDescription')
    labels = physical_description_section.find_all('span', class_='data-label')

    row_labels = {}

    for label in labels:
        if label.text.strip() != 'Hair Color' and label.text.strip() != 'Item' and label.text.strip() != 'Description':
            row_labels[label.text.strip()] = label.next_sibling.next_sibling.text.strip()
        else:
            row_labels[label.text.strip()] = label.next_sibling.strip()

    row['Hair Color'] = row_labels['Hair Color'] if 'Hair Color' in row_labels else print('Error finding column Hair Color')
    row['Head Hair Description'] = row_labels['Head Hair Description'] if 'Head Hair Description' in row_labels else print('Error finding column Head Hair Description')
    row['Body Hair Description'] = row_labels['Body Hair Description'] if 'Body Hair Description' in row_labels else print('Error finding column Body Hair Description')
    row['Facial Hair Description'] = row_labels['Facial Hair Description'] if 'Facial Hair Description' in row_labels else print('Error finding column Facial Hair Description')
    row['Left Eye Color'] = row_labels['Left Eye Color'] if 'Left Eye Color' in row_labels else print('Error finding column Left Eye Color')
    row['Right Eye Color'] = row_labels['Right Eye Color'] if 'Right Eye Color' in row_labels else print('Error finding column Right Eye Color')
    row['Eye Description'] = row_labels['Eye Description'] if 'Eye Description' in row_labels else print('Error finding column Eye Description')

    return row

def main():
    all_cases = pd.read_pickle(MISSING_PERSONS_FILE)
    global driver = SeleniumScraper.get_driver()

    case_additional_info = pd.DataFrame(columns=ADDITIONAL_INFO_COLUMNS)
    path = f'./data_files/case_additional_info{time.time()}.infer'

    for index, row in all_cases.iterrows():
        if index % 5 == 0: pdb.set_trace() # check after every 5 scrapes
        try:
            print(index)
            case_id = row['Case Number'][2:] # Case number format is "MP1234"

            case_info_row = pd.DataFrame(columns=ADDITIONAL_INFO_COLUMNS).append(pd.Series(dtype="object"), ignore_index=True)
            case_info_row['Case Number'] = row['Case Number']

            driver.get(f'https://www.namus.gov/MissingPersons/Case#/{case_id}/details?nav')

            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'Demographics'))
                )
            except Exception as e:
                print('could not find element after waiting 10 seconds')
                raise e

            case_info_row = scrape_demographics(case_info_row)
            case_info_row = scrape_circumstances(case_info_row)
            case_info_row = scrape_physical_description(case_info_row)

            case_additional_info = case_additional_info.append(case_info_row, ignore_index=True)
        except Exception as e:
            print(e)
            print(index, row)
            pdb.set_trace()
            case_additional_info.to_pickle(path)
    
    pdb.set_trace()
    case_additional_info.to_pickle(path)

if __name__ == '__main__':
    main()
