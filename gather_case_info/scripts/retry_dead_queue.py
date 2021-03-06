import boto3
import json
import pdb

def receive_message():
    client = boto3.client('sqs')
    response = client.receive_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers-dead-letter-queue',
        MaxNumberOfMessages=10
    )
    return response

def send_to_sqs(message):
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers',
        MessageBody=message
    )
    return response

def delete_sqs_message(message):
    client = boto3.client('sqs')
    response = client.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers-dead-letter-queue',
        ReceiptHandle=message["ReceiptHandle"]
    )
    return response

response = {'Messages': None}
while 'Messages' in response:
    response = receive_message()
    for message in response['Messages']:
        res1 = send_to_sqs(message['Body'])
        if res1['ResponseMetadata']['HTTPStatusCode'] == 200:
            res2 = delete_sqs_message(message)
            if res2['ResponseMetadata']['HTTPStatusCode'] != 200:
                print("couldn't delete", message)
            else:
                print("successfully sent to active queue and deleted from dead queue", message)
        elif res1['ResponseMetadata']['HTTPStatusCode'] != 200:
            print("couldn't send message", message)