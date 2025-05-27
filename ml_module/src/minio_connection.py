import boto3
from botocore.client import Config
import os
from io import BytesIO

from src.logger import logger

bucket_name = "model-bucket"

s3_client = boto3.client(
    service_name="s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id=os.environ.get('MINIO_ROOT_USER'),
    aws_secret_access_key=os.environ.get('MINIO_ROOT_PASSWORD'),
    config=Config(signature_version="s3v4"),
)

def create_bucket():
    try:
        s3_client.create_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Bucket {bucket_name} already exists or error occurred:", str(e))

def put_object(object_name : str, buffer : BytesIO):
    try:
        create_bucket()
        buffer.seek(0)
        s3_client.upload_fileobj(buffer, bucket_name, object_name)
        logger.debug(f"Saved {object_name} to {bucket_name} bucket")
    except Exception as e:
        logger.warning(f"Error while saving object: {e}")
        
        
def get_object(object_name : str):
    try:
        create_bucket()
        obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        body = obj['Body'].read()
    except Exception as e:
        logger.warning(f"Error while get object: {e}")
        body = None
    return body