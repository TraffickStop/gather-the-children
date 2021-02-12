import json
from scripts import namus
import sys
# def lambda_handler(event, context):
#     try:
#         test = namUs.main(['--date=>=February-1-2021'])
#     except Exception as e:
#         return {
#             'statusCode': 400,
#             'error': e
#         }
    
#     return {
#         'statusCode': 200,
#         'body': test
#     }

if __name__ == '__main__':
    namus.main(sys.argv[1:])