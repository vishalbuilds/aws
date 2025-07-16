import boto3
from common.logger import Logger

class S3Client:
    def __init__(self, region_name=None):
        self.logger = Logger(__name__)
        self.s3 = boto3.client('s3', region_name=region_name)

    def get_object(self, bucket, key):
        self.logger.info(f"Getting object from bucket: {bucket}, key: {key}")
        return self.s3.get_object(Bucket=bucket, Key=key)

    def put_object(self, bucket, key, body):
        self.logger.info(f"Putting object to bucket: {bucket}, key: {key}")
        return self.s3.put_object(Bucket=bucket, Key=key, Body=body)

    # Add more methods as needed 