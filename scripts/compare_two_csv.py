import csv
import json
import boto3

DYNAMODB_EXPORT_PATH = "/Users/spencerfitzgerald/export.my-table.csv"
NAMUS_EXPORT_PATH = "/Users/spencerfitzgerald/Desktop/School/IS 551 - UX Capstone/namus-export.csv"
SCRAPED_TO_DB_KEYS = {
    'Case Number': 'caseNumber',
    'DLC': 'dlc',
    'Last Name': 'lastName',
    'First Name': 'firstName',
    'Missing Age': 'missingAge',
    'City': 'city',
    'County': 'county',
    'State': 'state',
    'Sex': 'sex',
    'Race / Ethnicity': 'race',
    'Date Modified': 'dateModified'
}

def find_record_by_case_number(case_number, records):
    return next(item for item in records if item['Case Number'] == case_number)

def get_case_numbers(records, key='caseNumbers'):
    cases = []
    for record in records:
        cases.append(record.get(key))
    return cases

def get_list_of_records(csv_path):
    records = []

    with open(csv_path, "r", encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dict_row = dict(row)
            records.append(dict_row)

    return records

def send_to_sqs(record):
    print("Sending to SQS for case number: {0}".format(record['caseNumber']))
    message = json.dumps(record)
    client = boto3.client('sqs', region_name='us-east-1')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        MessageBody=message
    )
    print("Successfully sent message for: {0}".format(record['caseNumber']))

def main():
    dynamodb_records = get_list_of_records(DYNAMODB_EXPORT_PATH)
    namus_records = get_list_of_records(NAMUS_EXPORT_PATH)

    dynamodb_case_numbers = get_case_numbers(dynamodb_records, key='caseNumber')
    namus_case_numbers = get_case_numbers(namus_records, key='Case Number')

    unaccounted_cases = list(set(namus_case_numbers).difference(dynamodb_case_numbers))
    for case_number in unaccounted_cases:
        record = find_record_by_case_number(case_number, namus_records)
        message = {}
        for key in record:
            message[SCRAPED_TO_DB_KEYS[key]] = record[key]

        send_to_sqs(message)

main()
