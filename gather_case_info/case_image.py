import urllib

#CONSTANTS
S3_FILE_PATH = ''
NAMUS_URL_1 = 'https://www.namus.gov/MissingPersons/Case#/'
NAMUS_URL_2 = '/attachments'
NAMUS_IMAGE_XPATH = '//*[@id="visitor"]/div[1]/div[4]/div/div/section/div[1]/div/div/div/div[2]/div/div/div[2]/a[1]'

# Pass in Case number and Web Driver Instance
def store_namus_image(case_number, driver):
    try:
        url = NAMUS_URL_1+str(case_number)+NAMUS_URL_2
        driver.get(url)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, NAMUS_IMAGE_XPATH)))
        link = element.get_attribute('href')
        # Need to change file path to save to s3 here
        image_name = 'MP'+str(case_number)+'.jpg'
        urllib.request.urlretrieve(link, image_name)
        
        return 'success'

    except Exception as e:
        
        return e