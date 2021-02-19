import sys
from namus import main as gather_ids

def handler(event, context):
    try:
        gather_ids('February-1-2021')
        return {
            'statusCode': 200,
            'body': 'Successfully wrote to SQS',
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'error': e
        }
