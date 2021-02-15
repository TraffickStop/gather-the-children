import boto3
from case_info import main as add_additional_info
import pdb

def handler(event, context):
    try:
        case_info = context['message'] # message from sqs
        case_info = add_additional_info(case_info)
        # TODO: upload_image_to_s3(case_info)
        write_to_db(case_info)
        
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
    table = dynamodb.Table('People-o5msg6ojb5ahrlj5gj2g2aphsi-dev')
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


# {'Case Number': 'MP14787', 'DLC': '01/31/2006', 'Last Name': 'Smatlak', 'First Name': 'Donald', 'Missing Age': '25 Years', 'City': 'North Versailles', 'County': 'Allegheny County', 'State': 'PA', 'Sex': 'Male', 'Race': 'White / Caucasian', 'Date Modified': '04/03/2020', 'Current Age': '40 Years', 'Middle Name': 'David', 'Nickname': 'Donny', 'Height': '6\' 1"', 'Weight': '230 lbs', 'Date of Last Contact': 'January 31, 2006', 'NamUs Case Created': 'May 21, 2012', 'Location': 'North Versailles, Pennsylvania', 'Circumstances of Disappearance': 'Donald last had contact with family via phone at approximatley 4:00pm at his residence in the 1000 block of Logan Rd. in North Versailles, PA', 'Hair Color': 'Brown', 'Head Hair Description': '--', 'Body Hair Description': '--', 'Facial Hair Description': 'Goatee', 'Left Eye Color': 'Hazel', 'Right Eye Color': 'Hazel', 'Eye Description': '--', 'Namus Contact Name': 'Amy Jenkinson', 'Namus Phone Number': '(817) 304-8873', 'Namus Email': 'amy.jenkinson@unthsc.edu', 'Agency Name': 'North Versailles Police Department', 'Agency Investigator': None, 'Agency Address': '1401 Greensburg Avenue\r\nNorth Versailles, Pennsylvania 15137', 'Agency Type': 'Law Enforcement', 'Agency Main Phone': '(412) 823-9354', 'Agency General Email': '--', 'Agency Website URL': 'https://nvtpa.com/police/', 'Agency ORI': '--', 'Agency Jurisdiction': 'Local', 'Agency Case Number': '2006-00977', 'Agency Date Reported': '--', 'Agency Notes': '--', 'Agency County': 'Allegheny County'}