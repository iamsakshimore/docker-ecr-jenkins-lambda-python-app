import json
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

table = dynamodb.Table('ImageLogs')

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event, indent=2))
    
    detail = event.get("detail") or {}
    print("DETAIL:", json.dumps(detail, indent=2))
    
    # Extract image_tag with proper fallback logic
    image_tag = None
    
    # First try: look in detail object
    if isinstance(detail, dict) and detail:
        image_tag = detail.get("image-tag") or detail.get("image") or detail.get("imageTag")
        print(f"From detail: {image_tag}")
    
    # Second try: look in event root
    if not image_tag:
        image_tag = event.get("image_tag") or event.get("image") or event.get("imageTag")
        print(f"From event root: {image_tag}")
    
    # Final fallback
    if not image_tag:
        image_tag = "unknown-build"
        print("Using fallback: unknown-build")
    
    # Ensure it's a valid string
    image_tag = str(image_tag).strip()
    if not image_tag:
        image_tag = "unknown-build"
    
    timestamp = datetime.datetime.utcnow().isoformat()
    
    print(f"Final image_tag: '{image_tag}'")
    
    # Create item for DynamoDB
    item = {
        "image_tag": image_tag,
        "timestamp": timestamp
    }
    
    print("ITEM:", json.dumps(item, indent=2))
    
    try:
        table.put_item(Item=item)
        print("Successfully inserted into DynamoDB")
        
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:492711554489:ECRDeployment_Notifications',
            Subject='Docker Deployment Notification',
            Message=f"Image: {image_tag} deployed at {timestamp}"
        )
        print("Successfully sent SNS notification")
        
        return {
            "statusCode": 200,
            "body": json.dumps("Success")
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
