import json
import boto3
from keybert import KeyBERT

s3= boto3.client("s3")

def lambda_handler(event, context):
    bucket='keyrank-bucket'
    key='buff_file.json'
    
    response=s3.get_object(Bucket=bucket,Key=key)
    contents=response['Body']
    jsonobject=json.loads(contents.read())
    text=jsonobject['body']
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text)
    print(text)
