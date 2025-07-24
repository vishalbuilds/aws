import boto3
from common.logger import Logger

class TranscribeClient:
    def __init__(self, region_name=None):
        self.logger = Logger(__name__)
        self.transcribe = boto3.resource('transcribe', region_name=region_name)

    def start_transcription_job(self, transcription_job_name, media_file_uri, output_bucket, language_code='en-US'):
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
        self.logger.info(f"Getting transcription job status for: {transcription_job_name}")
        try:
            return self.transcribe.get_transcription_job(TranscriptionJobName=transcription_job_name)
        except Exception as e:
            self.logger.error(f"Error getting transcription job status: {e}")
            raise

    def delete_transcription_job(self, transcription_job_name):
        self.logger.info(f"Deleting transcription job status for: {transcription_job_name}")
        try:
             return self.transcribe.delete_transcription_job(TranscriptionJobName='transcription_job_name')
        except Exception as e:
            self.logger.error(f"Error deleting transcription job: {e}")
            raise

