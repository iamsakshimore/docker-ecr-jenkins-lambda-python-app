import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def lambda_handler(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    
    detail = event['detail']
    repository = detail['repository-name']
    tag = detail['image-tag'][0]
    timestamp = datetime.utcnow().isoformat()
    
    # DynamoDB - Fixed table name
    dynamo_success = False
    try:
        table = dynamodb.Table('ecr-deployments123')  # Changed from 'ecr-deployments'
        table.put_item(Item={
            'timestamp': timestamp,
            'repository': repository,
            'image_tag': tag
        })
        dynamo_success = True
        logger.info(" DynamoDB SUCCESS")
    except Exception as e:
        logger.error(f" DynamoDB ERROR: {str(e)}")
    
    # SNS
    sns_success = False
    try:
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:492711554489:ECRDeployment_Notifications',
            Message=f'{repository}:{tag} deployed at {timestamp}'
        )
        sns_success = True
        logger.info(" SNS SUCCESS")
    except Exception as e:
        logger.error(f" SNS ERROR: {str(e)}")
    
    return {
        'statusCode': 200 if dynamo_success and sns_success else 207,
        'body': json.dumps({
            'dynamo_success': dynamo_success,
            'sns_success': sns_success
        })
    }
