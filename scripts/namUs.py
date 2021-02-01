#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import pandas as pd
import getopt, pdb, re, sys, time

# CONSTANTS
CASE_NUMBER_KEY = 'Case Number'
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
MAX_ROWS_PER_PAGE = 100

# initialize global driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def apply_state_filters(states):
    print('Adding selected states to filter...')

    circumstances_section = driver.find_element_by_id('Circumstances')
    labels_in_section = circumstances_section.find_elements_by_tag_name('label')

    state_input_box = None

    for label in labels_in_section:
        if (label.text == "State"):
            state_input_box = label.find_element_by_tag_name('input')
            # add state filter
            for state in states:
                state_input_box.send_keys(state)
                state_input_box.send_keys(Keys.ENTER)

    action_buttons = driver.find_elements_by_class_name('button-box')[0].find_elements_by_tag_name('input')
    action_buttons[1].click()
    time.sleep(1.5)

def get_image_results():
    print('Gathering images...')

    # navigate to grid view
    driver.find_element_by_xpath("//i[@class=\"icon-grid-six\"]").click()
    time.sleep(1.5)

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

    return image_df

def get_info_results():
    print('Gathering info...')

    # navigate to list view
    driver.find_element_by_xpath("//i[@class=\"icon-list\"]").click()
    time.sleep(1.5)

    info_df = pd.DataFrame(columns=INFO_COLUMNS)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    rows = soup.find('div', class_='ui-grid-canvas').contents

    for row in rows:
        if row != ' ':
            cells = row.find_all('div', class_='ui-grid-cell-contents')
            cells_text = map(lambda cell: cell.text.strip(), cells)
            new_info_df = pd.DataFrame([list(cells_text)], columns=INFO_COLUMNS)
            info_df = info_df.append(new_info_df, ignore_index=True)
    
    return info_df

def parse_args(argv):
    help_message = 'Example usage: namUs.py --states=Utah,Arizona,California\n\nOptions:\n\t--states=: states flag; accepts a comma-separated list ie.(--states=Arizona,Utah,California)\n\t-h : Shows this help Screen; can also use --help'

    try:
        opts, args = getopt.getopt(argv,'h',['help', 'states='])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h','--help'):
            print(help_message)
            sys.exit()
        elif opt == '--states':
            return arg.split(',')

def rows_to_show(num_rows):
    print(f'Setting {MAX_ROWS_PER_PAGE} rows per page...')

    results_selection_dropdown = driver.find_element_by_xpath("//label/span[contains(text(),'Results')]/following-sibling::select")
    Select(results_selection_dropdown).select_by_value(f'{num_rows}')
    time.sleep(1.5)

def main(argv):
    states = parse_args(argv)
    
    print('Navigating to namus.gov...')
    driver.get("https://www.namus.gov/MissingPersons/Search")

    apply_state_filters(states)
    # TODO: for loop through the pages
    rows_to_show(MAX_ROWS_PER_PAGE)
    info_df = get_info_results()
    image_df = get_image_results()

    print('Merging Data...')
    merged_df = pd.merge(left=info_df, right=image_df, left_on=CASE_NUMBER_KEY, right_on=CASE_NUMBER_KEY)

    # TODO: send dataframe info to db
    driver.quit()

if __name__ == '__main__':
    main(sys.argv[1:])