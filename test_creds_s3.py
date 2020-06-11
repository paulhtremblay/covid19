#import os
import boto3
"""
key = os.environ['TEST_ACCESS_KEY_ID']
secret = os.environ['TEST_SECRET_ACCESS_KEY_ID']
client = boto3.client(
    's3',
    aws_access_key_id=key,
    aws_secret_access_key=secret,
)
"""

bucket_name = 'seattle-data-dev'
#client.put_object(Body = b'x', Bucket = bucket_name, Key = 'test')

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
bucket.put_object(Key = 'test', Body = b'x') 
