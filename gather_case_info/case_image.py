import requests
import boto3
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

#CONSTANTS
NAMUS_URL_1 = 'https://www.namus.gov/MissingPersons/Case#/'
NAMUS_URL_2 = '/attachments'
NAMUS_IMAGE_XPATH = '//*[@id="casesummary"]/div/div/div/div[2]/div[1]/img'
ORIGINAL = "Original"
THUMBNAIL = "Thumbnail"

# Pass in Case number and message
def upload_image_to_s3(case_number, message, driver):
    try:
        url = NAMUS_URL_1+str(case_number)+NAMUS_URL_2

        driver.get(url)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, NAMUS_IMAGE_XPATH)))
        link = element.get_attribute('src').replace(THUMBNAIL, ORIGINAL)

        if "Default" in link: return delete_sqs_message(message)

        r = requests.get(link, stream=True)

        return r.raw

    except Exception as e:
        raise

def delete_sqs_message(message):
    client = boto3.client('sqs')
    response = client.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        ReceiptHandle=message["receiptHandle"]
    )
    return "deleted message"