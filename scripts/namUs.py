#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import getopt, pdb, re, sys, time

# CONSTANTS
CASE_NUMBER_KEY = 'Case Number'
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
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def apply_filters(filters):
    if 'states' in filters: apply_state_filter(filters['states'])
    if 'date_operand' in filters: apply_date_filter(filters)

def apply_date_filter(date):
    print('Adding date filters...')

    circumstances_section = driver.find_element_by_id('Circumstances')
    operand_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[0]
    Select(operand_box).select_by_visible_text(date['date_operand'])

    time.sleep(.5)

    month_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[1]
    Select(month_box).select_by_visible_text(date['month'])

    day_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[2]
    Select(day_box).select_by_visible_text(date['day'])

    year_box = circumstances_section.find_elements_by_tag_name('date-range-input')[1].find_elements_by_tag_name('select')[3]
    Select(year_box).select_by_visible_text(date['year'])

def apply_state_filter(states):
    print('Adding selected states to filter...')

    circumstances_section = driver.find_element_by_id('Circumstances')
    labels_in_section = circumstances_section.find_elements_by_tag_name('label')

    for label in labels_in_section:
        if (label.text == "State"):
            state_input_box = label.find_element_by_tag_name('input')
            # add state filter
            for state in states:
                state_input_box.send_keys(state)
                state_input_box.send_keys(Keys.ENTER)

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

def get_page_numbers():
    print('Calculating number of pages...')
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    page_num_info = soup.find('nav', {'aria-label': 'Page Selection'}).find('span').text
    index_of_slash = re.search('/', page_num_info).span()[1]
    page_nums = int(page_num_info[index_of_slash:].strip())

    return page_nums

def next_page():
    print('clicking next page...')
    time.sleep(5)

    try:
        driver.find_element_by_xpath("//i[@class=\"icon-triangle-right\"]").click()
    except:
        print('last page completed...')

def parse_args(argv):
    help_message = """
    Example usage: namUs.py --states=Utah,Arizona,California
    Options:
        --states=:  States flag; accepts a comma-separated list ie.(--states=Arizona,Utah,California)
        -date=:     Date of Last Contact. Can search greater than or less than a given date
                    Example:    --date=">=January-5-1986" (sorts greater than the given date)
                                --date="<=January-5-1986" (sorts less than the given date)
        -h :        Shows this help Screen; can also use --help
    """
    filters = {}

    try:
        opts, args = getopt.getopt(argv,'h',['help', 'states=', 'date='])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h','--help'):
            print(help_message)
            sys.exit()
        if opt == '--states':
            filters['states'] = arg.split(',')
        if opt == '--date':
            filters['date_operand'] = arg[:2]
            filters['month'] = arg[2:].split('-')[0]
            filters['day'] = arg[2:].split('-')[1]
            filters['year'] = arg[2:].split('-')[2]

    return filters

def rows_to_show(num_rows):
    print(f'Setting {MAX_ROWS_PER_PAGE} rows per page...')

    results_selection_dropdown = driver.find_element_by_xpath("//label/span[contains(text(),'Results')]/following-sibling::select")
    Select(results_selection_dropdown).select_by_value(f'{num_rows}')
    time.sleep(1.5)

def search():
    print('Searching...')
    search_results_section = driver.find_element_by_class_name('search-criteria-container')
    search_actions = search_results_section.find_element_by_class_name('search-criteria-container-actions').find_elements_by_tag_name('input')
    search_actions[1].click()
    time.sleep(1.5)

def main(argv):
    filters = parse_args(argv)
    path = f'./data_files/states_missing_info{time.time()}.infer'

    print('Navigating to namus.gov...')
    driver.get("https://www.namus.gov/MissingPersons/Search")

    apply_filters(filters)
    search()

    rows_to_show(MAX_ROWS_PER_PAGE)
    page_nums = get_page_numbers()
    info_df = pd.DataFrame(columns=INFO_COLUMNS)

    try:
        for page in range(page_nums):
            print(f'starting page {page}...')
            new_df = get_info_results()
            info_df = info_df.append(new_df, ignore_index=True)
            next_page()
    except Exception as e:
        print(f'Exception thrown. Saving existing data to pickle: {path}')
        info_df.to_pickle(path)
        driver.quit()
        print(e)

    print(f'saving data to pickle: {path}')
    info_df.to_pickle(path)
    driver.quit()

    print('scraping completed')

if __name__ == '__main__':
    main(sys.argv[1:])