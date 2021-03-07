import sys
from namus import main as gather_ids
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ.get("LOGLEVEL", "INFO").upper()))

def handler(event, context):
    try:
        gather_ids(gt_date='June-2-2011', lt_date='April-1-2015')
        return {
            'statusCode': 200,
            'body': 'Successfully wrote to SQS',
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 400,
            'error': e
        }

# Date ranges
# gather_ids(lt_date='June-1-2011')
# gather_ids(gt_date='June-2-2011', lt_date='April-1-2015')
# gather_ids(gt_date='April-2-2015', lt_date='February-1-2019')
# gather_ids(gt_date='February-2-2019', lt_date='February-1-2021')
# gather_ids(gt_date='February-2-2021')
