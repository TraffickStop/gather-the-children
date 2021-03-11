import boto3
import json
import pdb

def receive_message():
    client = boto3.client('sqs')
    response = client.receive_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/694415534571/case-numbers-dead-letter-queue',
        MaxNumberOfMessages=1
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

while True:
    response = receive_message()
    for message in response['Messages']:
        print(message['Body'])