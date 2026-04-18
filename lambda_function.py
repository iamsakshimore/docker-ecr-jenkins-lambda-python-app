import json
import datetime

def lambda_handler(event, context):
    print("Event received:", json.dumps(event))

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Lambda triggered successfully',
            'time': str(datetime.datetime.now())
        })
    }