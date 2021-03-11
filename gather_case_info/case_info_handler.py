import boto3
from case_additional_info import main as add_additional_info
from case_image import get_image_response
import pdb
import uuid
import ast
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import logging

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

logger = logging.getLogger()
logger.setLevel(LOGLEVEL)

def handler(event, context):
    try:
        driver = init_driver()
        logger.info('Number of messages in batch: {0}'.format(len(event['Records'])))

        for record in event.get('Records'):
            try:
                case_info = record.get("body")

                case_info = json.loads(case_info)
                if type(case_info) == type(''):
                    logger.debug('Type of case_info was string. Attempting to convert to dict...')
                    case_info = json.loads(case_info)
                logger.debug('Type of case_info variable: {0}'.format(type(case_info)))

                img_response = get_image_response(case_info["caseNumber"][2:], record, driver)
                if img_response == "delete message":
                    remove_from_queue(record)
                    logger.info("No photo uploaded for {0}".format(case_info["caseNumber"]))
                    continue
    
                case_info = add_additional_info(case_info, driver)

                write_to_db_and_s3(case_info, img_response)
                remove_from_queue(record)

                logger.info("Successfully uploaded photo and wrote to DB for {0}".format(case_info["caseNumber"]))
            except Exception as e:
                remove_from_queue(record)
                send_to_dead_queue(record)
                logger.exception("Exception thrown for {0}: {1}".format(case_info["caseNumber"], e))
                continue

        driver.quit()
        return {
            'statusCode': 200,
            'body': 'success'
        }
    except Exception as e:
        logger.exception("Exception: {0}".format(e))

        return {
            'statusCode': 400,
            'error': e,
            'body': 'failed'
        }

def init_driver():
    logger.debug('Initializing driver...')
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome('/opt/chromedriver', chrome_options=options)
    logger.debug('Driver initialized...')
    return driver

def remove_from_queue(message):
    logger.info("Removing from queue")
    client = boto3.client('sqs')
    response = client.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        ReceiptHandle=message["receiptHandle"]
    )

def send_to_dead_queue(message):
    logger.info("Sending to dead queue {0}".format(message['body']))
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers-dead-letter-queue',
        MessageBody=message['body']
    )

def write_to_db_and_s3(record, image):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('People-o5msg6ojb5ahrlj5gj2g2aphsi-dev')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('traffick-stop-namus-missing-persons-images')
    
    record['id'] = str(uuid.uuid4())
    record['createdAt'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # Upload at the same time to avoid one working without the other
    table.put_item(Item=record)
    logger.debug("Uploaded {0} to db".format(record))
    bucket.upload_fileobj(image, record['caseNumber']+'.jpg')
    logger.debug(f"Uploaded {0}.jpg to s3".format(record["caseNumber"]))
