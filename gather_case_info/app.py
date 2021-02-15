import boto3
import case_info.main as add_additional_info
import pdb

def handler(event, context):
    try:
        case_info = context.message # message from sqs
        case_info = add_additional_info(case_info)
        # TODO: upload_image_to_s3(case_info)
        # TODO: write_to_db(case_info)
        
        pdb.set_trace()
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
    table = dynamodb.Table('users')
    table.put_item(Item=record)

context = {
    'message': {
        'Case Number': 'MP14787',
        'DLC': '01/31/2006',
        'Last Name': 'Smatlak',
        'First Name': 'Donald',
        'Missing Age': '25 Years',
        'City': 'North Versailles',
        'County': 'Allegheny',
        'State': 'PA',
        'Sex': 'Male',
        'Race': 'White / Caucasian',
        'Date Modified': '04/03/2020'
    }
}

handler(None, context)