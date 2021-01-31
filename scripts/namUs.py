from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
from bs4 import BeautifulSoup
import pandas as pd
import pdb

# constants
STATES = ['Utah']
COLUMNS = [
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
driver.get("https://www.namus.gov/MissingPersons/Search")
circumstances_section = driver.find_element_by_id('Circumstances')
labels_in_section = circumstances_section.find_elements_by_tag_name('label')

state_input_box = None

for label in labels_in_section:
    if (label.text == "State"):
        state_input_box = label.find_element_by_tag_name('input')
        # add state filter
        for state in STATES:
            state_input_box.send_keys(state)
            state_input_box.send_keys(Keys.ENTER)

# navigate to list view
action_buttons = driver.find_elements_by_class_name('button-box')[0].find_elements_by_tag_name('input')
action_buttons[1].click()

# show 100 results at a time
time.sleep(1.5)
results_selection_dropdown = driver.find_element_by_xpath("//label/span[contains(text(),'Results')]/following-sibling::select")
Select(results_selection_dropdown).select_by_value('100')
time.sleep(1.5)

# get row results and store in dataframes
df = pd.DataFrame(columns=COLUMNS)
soup = BeautifulSoup(driver.page_source, 'lxml')
rows = soup.find('div', class_='ui-grid-canvas').contents

for row in rows:
    if row != ' ':
        cells = row.find_all('div', class_='ui-grid-cell-contents')
        cells_text = map(lambda cell: cell.text.strip(), cells)
        new_df = pd.DataFrame([list(cells_text)], columns=COLUMNS)
        df = df.append(new_df, ignore_index=True)

pdb.set_trace()
# navigate to grid view
driver.find_element_by_xpath("//i[@class=\"icon-grid-six\"]").click()

# find href and merge into record with matching NamUs ID

# print records to csv

missing_persons = []

for review_selector in reviews_selector:
    review_div = review_selector.find('div', class_='dyn_full_review')
    if review_div is None:
        review_div = review_selector.find('div', class_='basic_review')
    review = review_div.find('div', class_='entry').find('p').get_text()
    review = review.strip()
    reviews.append(review)

driver.quit()