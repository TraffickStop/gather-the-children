import sys
from namus import main as gather_ids

def handler(event, context):
    try:
        gather_ids(lt_date='June-1-2011')
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

# gather_ids(lt_date='June-1-2011')
# gather_ids(gt_date='April-16-2015', lt_date='February-15-2021')
# gather_ids(gt_date='April-16-2015', lt_date='February-15-2021')
# gather_ids(gt_date='February-16-2021')
