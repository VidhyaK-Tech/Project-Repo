import json
import boto3
import urllib.parse
import time

s3 = boto3.client('s3')
sns = boto3.client('sns')

def lambda_handler(event, context):
    for record in event['Records']:
        
        # Step 1: Get SQS message body
        body = json.loads(record['body'])
        
        # Step 2: Get S3 event
        s3_event = body['Records'][0]
        
        bucket_name = s3_event['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(s3_event['s3']['object']['key'])
        
        print("Bucket:", bucket_name)
        print("File:", object_key)

        # Step 3: Read file from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')

        print("Original Content:", file_content)

        # Step 4: Process
        processed_data = file_content.upper()

        print("Processing done, going to save file...")
        print("Saving to output bucket...")
        
        # Step 5: Create unique output key
        filename = object_key.split('/')[-1].replace('.txt', '')
        output_key = f'output-{filename}-{int(time.time())}.txt'
        # Step 6: Save to output bucket
        s3.put_object(
            Bucket='output-bucket-singapore1',
            Key=output_key,
            Body=processed_data,
            ContentType='text/plain'
        )

        print("Saved file:", output_key)

        # Step 7: Generate Pre-Signed URL
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': 'output-bucket-singapore1', 'Key': output_key},
            ExpiresIn=3600
        )

        print("Pre-Signed URL:", url)

        # Step 8: Send SNS Email
        sns.publish(
            TopicArn='arn:aws:sns:ap-southeast-1:543687745943:output-alert',
            Message=f'File ready: {url}',
            Subject='S3 Output Ready'
        )

    return {
        'statusCode': 200,
        'body': 'Processing Done'
    }