import boto3
from case_info import main as add_additional_info
import pdb
import uuid

def handler(event, context):
    try:
        case_info = context['message'] # TODO: message from sqs
        case_info = add_additional_info(case_info)
        # TODO: upload_image_to_s3(case_info)
        write_to_db(case_info)
        
        return {
            'statusCode': 200,
            'body': case_info
        }
    except Exception as e:
        pdb.set_trace()
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
