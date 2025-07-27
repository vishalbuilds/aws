"""
s3_remove_pii.py: Lambda handler for removing PII from S3 audio files using AWS Transcribe.

This handler uses S3 and Transcribe utility classes from the utils/ folder for all AWS operations.
It demonstrates OOP, logging, and robust error handling.
"""
import uuid
import time
import os
from src.strategies.utils.s3_utils import S3Utils
from src.strategies.utils.transcribe_utils import TranscribeUtils
from common.logger import Logger

class S3RemovePii(S3Utils, TranscribeUtils):
    """
    Handler for removing PII from S3 audio files using AWS Transcribe.
    Inherits S3Utils and TranscribeUtils for AWS operations.
    """
    def __init__(self):
        S3Utils.__init__(self, region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        TranscribeUtils.__init__(self, region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        self.logger = Logger(__name__)
        self.target_output_bucket = os.environ.get('TARGET_OUTPUT_BUCKET', 'new-recording-with-pii')

    def generate_random_id(self):
        """Generate a random UUID string."""
        self.logger.info('Generating random ID')
        try:
            return str(uuid.uuid4())
        except Exception as e:
            self.logger.error(f"Error generating random ID: {e}")
            raise e

    def handle(self, event, context):
        """
        Lambda entry point for removing PII from S3 audio files.
        Args:
            event (dict): Lambda event payload.
            context: Lambda context object.
        Returns:
            dict: Lambda response with status and message.
        """
        self.logger.info('Lambda handler function')
        self.logger.info(f" Starting LambdaFunctionName:redact-pii, Region: {self.s3.meta.region_name}")
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        media_file_uri = f"s3://{source_bucket}/{source_key}"
        transcription_job_name = f"Transcription_Job_Name-{self.generate_random_id()}"
        try:
            # Example usage of inherited S3Utils method (get_object):
            # obj = self.get_object(source_bucket, source_key)
            transcription_start = self.start_transcription_job(
                transcription_job_name, media_file_uri, self.target_output_bucket)
            transcription_start_status = transcription_start['TranscriptionJob']['TranscriptionJobStatus']
            if transcription_start_status in ['IN_PROGRESS', 'QUEUED']:
                time.sleep(5)
                check_status = self.check_transcription_status(transcription_job_name)
                self.logger.info(f"Transcription job processing completed with status: {check_status}")
                return {
                    'statusCode': 200,
                    'message': 'Transcription job processing completed',
                    'media_file_uri': f"s3://{source_bucket}/{source_key}",
                    'Status': check_status
                }
            elif transcription_start_status in ['COMPLETED']:
                self.logger.error(f"Transcription job processing completed with status: {transcription_start_status}")
                return {
                    'statusCode': 200,
                    'message': 'Transcription job processing completed',
                    'media_file_uri': f"s3://{source_bucket}/{source_key}",
                    'Status': transcription_start_status
                }
            elif transcription_start_status in ['FAILED']:
                self.logger.error(f"Transcription job processing failed with status: {transcription_start_status}")
                return {
                    'statusCode': 400,
                    'message': 'Transcription job processing failed',
                    'media_file_uri': f"s3://{source_bucket}/{source_key}",
                    'Status': transcription_start_status
                }
            else:
                self.logger.error("Transcription job processing not found with status")
                return {
                    'statusCode': 400,
                    'message': 'Transcription job processing not found',
                    'media_file_uri': f"s3://{source_bucket}/{source_key}",
                    'Status': 'UNKNOWN'
                }
        except Exception as e:
            self.logger.error(f"Error processing file {media_file_uri}, Error: {e}")
            return {
                'statusCode': 400,
                'message': 'Error processing file',
                'error': str(e),
                'media_file_uri': f"s3://{source_bucket}/{source_key}",
            }

