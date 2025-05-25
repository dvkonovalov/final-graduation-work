import boto3
from botocore.client import Config
import os
from io import BytesIO

from src.logger import logger

s3_client = boto3.client(
    service_name="s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id=os.environ.get('MINIO_ROOT_USER'),
    aws_secret_access_key=os.environ.get('MINIO_ROOT_PASSWORD'),
    config=Config(signature_version="s3v4"),
)


bucket_name = "model-bucket"
try:
    s3_client.create_bucket(Bucket=bucket_name)
except Exception as e:
    print(f"Bucket {bucket_name} already exists or error occurred:", str(e))

def put_object(object_name : str, buffer : BytesIO):
    response = s3_client.upload_fileobj(buffer, bucket_name, object_name)

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.debug("File uploaded successfully.")
    else:
        logger.debug("Error uploading file.")
        
def get_object(object_name : str):
    obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
    body = obj['Body'].read()
    logger.debug(body)
    return body