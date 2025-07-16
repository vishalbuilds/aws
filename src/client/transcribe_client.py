import boto3
from common.logger import Logger

class TranscribeClient:
    """
    AWS Transcribe client for starting and checking transcription jobs.
    """
    def __init__(self, region_name=None):
        self.logger = Logger(__name__)
        self.transcribe = boto3.client('transcribe', region_name=region_name)

    def start_transcription_job(self, transcription_job_name, media_file_uri, output_bucket, language_code='en-US'):
        """
        Start a transcription job with PII redaction.
        Args:
            transcription_job_name (str): Name for the transcription job.
            media_file_uri (str): S3 URI of the media file.
            output_bucket (str): S3 bucket for output.
            language_code (str): Language code (default 'en-US').
        Returns:
            dict: Response from start_transcription_job.
        """
        self.logger.info(f"Starting transcription job: {transcription_job_name} for file: {media_file_uri}")
        try:
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=transcription_job_name,
                LanguageCode=language_code,
                Media={'MediaFileUri': media_file_uri},
                ContentRedaction={'RedactionType': 'PII', 'RedactionOutput': 'redacted'},
                OutputBucketName=output_bucket,
            )
            return response
        except Exception as e:
            self.logger.error(f"Error starting transcription job: {e}")
            raise

    def get_transcription_job(self, transcription_job_name):
        """
        Get the status of a transcription job.
        Args:
            transcription_job_name (str): Name of the transcription job.
        Returns:
            dict: Response from get_transcription_job.
        """
        self.logger.info(f"Getting transcription job status for: {transcription_job_name}")
        try:
            return self.transcribe.get_transcription_job(TranscriptionJobName=transcription_job_name)
        except Exception as e:
            self.logger.error(f"Error getting transcription job status: {e}")
            raise

    def check_transcription_status(self, transcription_job_name):
        """
        Poll the status of a transcription job until it completes or fails.
        Args:
            transcription_job_name (str): Name of the transcription job.
        Returns:
            str: Final status ('COMPLETED', 'FAILED', or 'UNKNOWN').
        """
        self.logger.info(f"Checking transcription job status for: {transcription_job_name}")
        try:
            while True:
                response = self.get_transcription_job(transcription_job_name)
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                self.logger.info(f"Transcription job status: {status}")
                if status == 'COMPLETED':
                    self.logger.info(f"Transcription job completed with status: {status}")
                    return status
                elif status == 'IN_PROGRESS':
                    self.logger.info("Transcription job in progress...")
                    import time
                    time.sleep(5)
                elif status == 'FAILED':
                    self.logger.error(f"Transcription job failed: {status}")
                    return status
                else:
                    self.logger.error(f"Transcription job status not found: {response}")
                    return "UNKNOWN"
        except Exception as e:
            self.logger.error(f"Error checking transcription job status: {e}")
            raise 