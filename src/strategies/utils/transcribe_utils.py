"""
TranscribeUtils: A comprehensive utility class for AWS Transcribe operations.

This class provides high-level, descriptive methods for starting, getting, and checking transcription jobs.
All methods include logging and error handling for robust production use.
"""
from src.common.client.transcribe_client import TranscribeClient


class TranscribeUtils(TranscribeClient):

    def check_transcription_status(self, transcription_job_name):
        """
        Poll the status of a transcription job until it completes or fails.
        Args:
            transcription_job_name (str): Name of the transcription job.
        Returns:
            str: Final status ('COMPLETED', 'FAILED', or 'UNKNOWN').
        Raises:
            Exception: If the operation fails.
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