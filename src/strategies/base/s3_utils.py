"""
S3Utils: A comprehensive utility class for AWS S3 operations.

This class provides high-level, descriptive methods for common S3 operations such as get, put, delete, and list objects.
All methods include logging and error handling for robust production use.
"""
import boto3
from common.logger import Logger
import os

class S3Utils:
    """
    Utility class for AWS S3 operations with descriptive, robust methods.
    """
    def __init__(self, region_name=None):
        """
        Initialize the S3Utils class with region and logger.
        """
        self.logger = Logger(__name__)
        self.s3 = boto3.client('s3', region_name=region_name or os.environ.get('AWS_REGION', 'us-east-1'))

    def get_object(self, bucket, key):
        """
        Get an object from an S3 bucket.
        Args:
            bucket (str): The name of the S3 bucket.
            key (str): The object key.
        Returns:
            dict: The response from S3 get_object.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Getting object from bucket: {bucket}, key: {key}")
        try:
            return self.s3.get_object(Bucket=bucket, Key=key)
        except Exception as e:
            self.logger.error(f"Error getting object: {e}")
            raise

    def put_object(self, bucket, key, body):
        """
        Put an object into an S3 bucket.
        Args:
            bucket (str): The name of the S3 bucket.
            key (str): The object key.
            body (bytes or str): The content to upload.
        Returns:
            dict: The response from S3 put_object.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Putting object to bucket: {bucket}, key: {key}")
        try:
            return self.s3.put_object(Bucket=bucket, Key=key, Body=body)
        except Exception as e:
            self.logger.error(f"Error putting object: {e}")
            raise

    def delete_object(self, bucket, key):
        """
        Delete an object from an S3 bucket.
        Args:
            bucket (str): The name of the S3 bucket.
            key (str): The object key.
        Returns:
            dict: The response from S3 delete_object.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Deleting object from bucket: {bucket}, key: {key}")
        try:
            return self.s3.delete_object(Bucket=bucket, Key=key)
        except Exception as e:
            self.logger.error(f"Error deleting object: {e}")
            raise

    def list_objects(self, bucket, prefix=None):
        """
        List objects in an S3 bucket, optionally filtered by prefix.
        Args:
            bucket (str): The name of the S3 bucket.
            prefix (str, optional): Prefix to filter objects.
        Returns:
            dict: The response from S3 list_objects_v2.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Listing objects in bucket: {bucket}, prefix: {prefix}")
        try:
            kwargs = {'Bucket': bucket}
            if prefix:
                kwargs['Prefix'] = prefix
            return self.s3.list_objects_v2(**kwargs)
        except Exception as e:
            self.logger.error(f"Error listing objects: {e}")
            raise 