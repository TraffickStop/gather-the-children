import boto3
import case_additional_info.main as add_additional_info
import case_contact_info.main as add_contact_info

def handler(event, context):
    error = None
    status_code = 200
    ip = None

    try:
        case_info = context.message # message from sqs
        case_info = add_additional_info(case_info)
        case_info = add_contact_info(case_info)
        # TODO: case_info = add_image_paths(case_info)
        # TODO: upload_image_to_s3(case_info)
        write_to_db(case_info)
    except Exception as e:
        status_code = 400
        error = e
        print(error)

    return {
        'statusCode': status_code,
        'body': ip,
        'error': error
    }

def write_to_db(record):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    table.put_item(Item=record)

# TODO: def upload_image_to_s3(record):
    # upload image to s3 and

handler(None, None)