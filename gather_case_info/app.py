import sys
import namus

def handler(event, context):
    error = None
    status_code = 200
    ip = None

    try:
        ip = namus.main(['--date=>=February-1-2021'])
    except Exception as e:
        status_code = 400
        error = e
    print(ip)
    return {
        'statusCode': status_code,
        'body': ip,
        'error': error
    }

handler(None, None)