#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
from bs4 import BeautifulSoup
import pandas as pd
import pdb
import re

# constants
STATES = ['Utah']
IMG_COLUMNS = [
    'Case Number',
    'Image Link'
]
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

# initialize driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# find state filter
print('navigating to namus.gov...')
driver.get("https://www.namus.gov/MissingPersons/Search")
circumstances_section = driver.find_element_by_id('Circumstances')
labels_in_section = circumstances_section.find_elements_by_tag_name('label')

state_input_box = None

print('Adding selected states to filter...')
for label in labels_in_section:
    if (label.text == "State"):
        state_input_box = label.find_element_by_tag_name('input')
        # add state filter
        for state in STATES:
            state_input_box.send_keys(state)
            state_input_box.send_keys(Keys.ENTER)

# navigate to list view
action_buttons = driver.find_elements_by_class_name('button-box')[0].find_elements_by_tag_name('input')
print('Searching...')
action_buttons[1].click()

# show 100 results at a time
time.sleep(1.5)
results_selection_dropdown = driver.find_element_by_xpath("//label/span[contains(text(),'Results')]/following-sibling::select")
print('Selecting 100 results...')
Select(results_selection_dropdown).select_by_value('100')
time.sleep(1.5)

# get row results and store in dataframes
info_df = pd.DataFrame(columns=INFO_COLUMNS)
soup = BeautifulSoup(driver.page_source, 'lxml')
rows = soup.find('div', class_='ui-grid-canvas').contents

print('Gathering info...')
for row in rows:
    if row != ' ':
        cells = row.find_all('div', class_='ui-grid-cell-contents')
        cells_text = map(lambda cell: cell.text.strip(), cells)
        new_info_df = pd.DataFrame([list(cells_text)], columns=INFO_COLUMNS)
        info_df = info_df.append(new_info_df, ignore_index=True)

# navigate to grid view
# find href and merge into record with matching NamUs ID
driver.find_element_by_xpath("//i[@class=\"icon-grid-six\"]").click()
time.sleep(1.5)
print('Gathering images...')
image_df = pd.DataFrame(columns=IMG_COLUMNS)
soup = BeautifulSoup(driver.page_source, 'lxml')
rows = soup.find('search-results-gallery').find_all('div', class_='card-stack')

for row in rows:
    img_src = 'namus.gov' + row.find('img')['src']
    case_number_line = row.find('div', class_='top-row').find('span', class_='data-label').text.strip()
    case_number_start = re.search('#',case_number_line).span()[1]
    case_number = case_number_line[case_number_start:]
    new_img_df = pd.DataFrame([[case_number, img_src]], columns=IMG_COLUMNS)
    image_df = image_df.append(new_img_df, ignore_index=True)

# merge image source with info
print('Merging Data...')
merged_df = pd.merge(left=info_df, right=image_df, left_on='Case Number', right_on='Case Number')

pdb.set_trace()

# print records to csv
driver.quit()