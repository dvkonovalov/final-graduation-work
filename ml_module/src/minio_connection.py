import boto3
from botocore.client import Config
import os

s3_client = boto3.client(
    service_name="s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id=os.environ.get('MINIO_ROOT_USER'),
    aws_secret_access_key=os.environ.get('MINIO_ROOT_PASSWORD'),
    config=Config(signature_version="s3v4"),
)


bucket_name = "test-bucket"
try:
    s3_client.create_bucket(Bucket=bucket_name)
except Exception as e:
    print(f"Bucket {bucket_name} already exists or error occurred:", str(e))

object_name = "example.txt"
content = "Hello from MinIO!"
response = s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=content.encode())

if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    print("File uploaded successfully.")
else:
    print("Error uploading file.")

# Теперь считываем этот файл обратно
obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
body = obj['Body'].read().decode('utf-8')
print(body)