import boto3
from case_additional_info import main as add_additional_info
import pdb
import uuid

def handler(event, context):
    print(event["Records"])
    try:
        for record in event['Records']:
            case_info = record["body"]
            case_info = add_additional_info(case_info)
            # TODO: upload_image_to_s3(case_info)
            write_to_db(case_info)

        return {
            'statusCode': 200,
            'body': "successfully uploaded data to dynamodb and s3"
        }
    except Exception as e:
        print(e)

        return {
            'statusCode': 400,
            'error': e
        }

def write_to_db(record):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('People-o5msg6ojb5ahrlj5gj2g2aphsi-dev')
    record['id'] = str(uuid.uuid4())
    table.put_item(Item=record)
