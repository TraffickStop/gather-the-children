import boto3
from case_additional_info import main as add_additional_info
from case_image import upload_image_to_s3
import pdb
import uuid
import ast
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

def handler(event, context):
    try:
        body = ""
        driver = init_driver()
        print('Number of messages in batch: ', len(event['Records']))
        for record in event['Records']:
            try:
                case_info = record["body"]
                if type(case_info) == type(''): case_info = ast.literal_eval(case_info)

                img_response = upload_image_to_s3(case_info["caseNumber"][2:], record, driver)
                if img_response == "deleted message":
                    body = body + f'No photo uploaded for {case_info["caseNumber"]}\n'
                    remove_from_queue(record)
                    continue
    
                case_info = add_additional_info(case_info, driver)

                write_to_db_and_s3(case_info, img_response)
                body = body + f'Successfully uploaded photo and wrote to DB for {case_info["caseNumber"]}\n'

                remove_from_queue(record)
            except Exception as e:
                body = body + f'Exception thrown for {case_info["caseNumber"]}: {e}\n'
                
                remove_from_queue(record)
                send_to_dead_queue(record)
                continue

        driver.quit()
        print("Body:", body)
        return {
            'statusCode': 200,
            'body': body
        }
    except Exception as e:
        print("Exception:", e)
        print("Body:", body)

        return {
            'statusCode': 400,
            'error': e,
            'body': body
        }

def init_driver():
    # print('Initializing driver...')
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome('/opt/chromedriver', chrome_options=options)
    # print('Driver initialized...')
    return driver

def remove_from_queue(message):
    # print("removing from queue")
    client = boto3.client('sqs')
    response = client.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        ReceiptHandle=message["receiptHandle"]
    )

def send_to_dead_queue(message):
    # print("sending to dead queue")
    body = json.dumps(message['body'])
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers-dead-letter-queue',
        MessageBody=body
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
    bucket.upload_fileobj(image, record['caseNumber']+'.jpg')
