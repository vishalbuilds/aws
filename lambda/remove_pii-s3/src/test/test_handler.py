import unittest
from unittest.mock import patch, MagicMock
import os
import json
import boto3
from botocore.stub import Stubber
import sys
import uuid
import time

# Import the module to test
# Mocking the module path import
sys.modules['....common.logger'] = MagicMock()
from remove_pii import generate_random_id, start_transcription_job, get_transcription_job_status, check_transcription_status, lambda_handler


class TestTranscribeLambda(unittest.TestCase):

    def setUp(self):
        # Setup environment variables
        os.environ['AWS_REGION'] = 'us-east-1'
        os.environ['TARGET_OUTPUT_BUCKET'] = 'test-output-bucket'

        # Mock event data
        self.event = {
            'Records': [
                {
                    's3': {
                        'bucket': {
                            'name': 'test-source-bucket'
                        },
                        'object': {
                            'key': 'test-recording.mp3'
                        }
                    }
                }
            ]
        }

        # Mock context
        self.context = MagicMock()

        # UUID mock to ensure predictable IDs
        self.mock_uuid = "12345678-1234-5678-1234-567812345678"

    @patch('uuid.uuid4')
    def test_generate_random_id(self, mock_uuid):
        mock_uuid.return_value = self.mock_uuid
        result = generate_random_id()
        self.assertEqual(result, str(self.mock_uuid))

    @patch('boto3.client')
    def test_start_transcription_job_success(self, mock_boto3_client):
        # Setup mock
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        mock_response = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'test-job',
                'TranscriptionJobStatus': 'IN_PROGRESS'
            }
        }
        mock_client.start_transcription_job.return_value = mock_response

        # Test function
        result = start_transcription_job(
            'test-job',
            's3://test-bucket/test-file.mp3',
            'test-output-bucket'
        )

        # Assertions
        self.assertEqual(result, mock_response)
        mock_client.start_transcription_job.assert_called_once_with(
            TranscriptionJobName='test-job',
            LanguageCode='en-US',
            Media={'MediaFileUri': 's3://test-bucket/test-file.mp3'},
            ContentRedaction={'RedactionType': 'PII', 'RedactionOutput': 'redacted'},
            OutputBucketName='test-output-bucket'
        )

    @patch('boto3.client')
    def test_start_transcription_job_exception(self, mock_boto3_client):
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.start_transcription_job.side_effect = Exception("Test error")

        # Test exception handling
        with self.assertRaises(Exception):
            start_transcription_job(
                'test-job',
                's3://test-bucket/test-file.mp3',
                'test-output-bucket'
            )

    @patch('boto3.client')
    def test_get_transcription_job_status_success(self, mock_boto3_client):
        # Setup mock
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        mock_response = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'test-job',
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }
        mock_client.get_transcription_job.return_value = mock_response

        # Test function
        result = get_transcription_job_status('test-job')

        # Assertions
        self.assertEqual(result, mock_response)
        mock_client.get_transcription_job.assert_called_once_with(
            TranscriptionJobName='test-job'
        )

    @patch('boto3.client')
    def test_get_transcription_job_status_exception(self, mock_boto3_client):
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.get_transcription_job.side_effect = Exception("Test error")

        # Test exception handling
        with self.assertRaises(Exception):
            get_transcription_job_status('test-job')

    @patch('time.sleep', return_value=None)
    @patch('lambda_function.get_transcription_job_status')
    def test_check_transcription_status_completed(self, mock_get_status, mock_sleep):
        # Setup mock
        mock_get_status.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }

        # Test function
        result = check_transcription_status('test-job')

        # Assertions
        self.assertEqual(result, 'COMPLETED')
        mock_get_status.assert_called_once_with('test-job')
        mock_sleep.assert_not_called()

    @patch('time.sleep', return_value=None)
    @patch('lambda_function.get_transcription_job_status')
    def test_check_transcription_status_failed(self, mock_get_status, mock_sleep):
        # Setup mock
        mock_get_status.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'FAILED'
            }
        }

        # Test function
        result = check_transcription_status('test-job')

        # Assertions
        self.assertEqual(result, 'FAILED')
        mock_get_status.assert_called_once_with('test-job')
        mock_sleep.assert_not_called()

    @patch('time.sleep', return_value=None)
    @patch('lambda_function.get_transcription_job_status')
    def test_check_transcription_status_in_progress_then_completed(self, mock_get_status, mock_sleep):
        # Setup mock to return IN_PROGRESS once, then COMPLETED
        mock_get_status.side_effect = [
            {
                'TranscriptionJob': {
                    'TranscriptionJobStatus': 'IN_PROGRESS'
                }
            },
            {
                'TranscriptionJob': {
                    'TranscriptionJobStatus': 'COMPLETED'
                }
            }
        ]

        # Test function
        result = check_transcription_status('test-job')

        # Assertions
        self.assertEqual(result, 'COMPLETED')
        self.assertEqual(mock_get_status.call_count, 2)
        mock_sleep.assert_called_once_with(5)

    @patch('time.sleep', return_value=None)
    @patch('lambda_function.get_transcription_job_status')
    def test_check_transcription_status_unknown(self, mock_get_status, mock_sleep):
        # Setup mock to return unknown status
        mock_get_status.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'SOME_UNKNOWN_STATUS'
            }
        }

        # Test function
        result = check_transcription_status('test-job')

        # Assertions
        self.assertEqual(result, 'UNKNOWN')
        mock_get_status.assert_called_once_with('test-job')
        mock_sleep.assert_not_called()

    @patch('lambda_function.check_transcription_status')
    @patch('lambda_function.start_transcription_job')
    @patch('lambda_function.generate_random_id')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_success_in_progress(self, mock_sleep, mock_id, mock_start, mock_check):
        # Setup mocks
        mock_id.return_value = self.mock_uuid
        mock_start.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'IN_PROGRESS'
            }
        }
        mock_check.return_value = 'COMPLETED'

        # Test function
        result = lambda_handler(self.event, self.context)

        # Assertions
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['Status'], 'COMPLETED')
        mock_id.assert_called_once()
        mock_start.assert_called_once_with(
            f"Transcription_Job_Name-{self.mock_uuid}",
            "s3://test-source-bucket/test-recording.mp3",
            "test-output-bucket"
        )
        mock_check.assert_called_once_with(f"Transcription_Job_Name-{self.mock_uuid}")
        mock_sleep.assert_called_once_with(5)

    @patch('lambda_function.start_transcription_job')
    @patch('lambda_function.generate_random_id')
    def test_lambda_handler_success_completed(self, mock_id, mock_start):
        # Setup mocks
        mock_id.return_value = self.mock_uuid
        mock_start.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }

        # Test function
        result = lambda_handler(self.event, self.context)

        # Assertions
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['Status'], 'COMPLETED')
        mock_id.assert_called_once()
        mock_start.assert_called_once()

    @patch('lambda_function.start_transcription_job')
    @patch('lambda_function.generate_random_id')
    def test_lambda_handler_failed(self, mock_id, mock_start):
        # Setup mocks
        mock_id.return_value = self.mock_uuid
        mock_start.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'FAILED'
            }
        }

        # Test function
        result = lambda_handler(self.event, self.context)

        # Assertions
        self.assertEqual(result['statusCode'], 400)
        self.assertEqual(result['Status'], 'FAILED')
        mock_id.assert_called_once()
        mock_start.assert_called_once()

    @patch('lambda_function.start_transcription_job')
    @patch('lambda_function.generate_random_id')
    def test_lambda_handler_unknown_status(self, mock_id, mock_start):
        # Setup mocks
        mock_id.return_value = self.mock_uuid
        mock_start.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'SOME_UNKNOWN_STATUS'
            }
        }

        # Test function
        result = lambda_handler(self.event, self.context)

        # Assertions
        self.assertEqual(result['statusCode'], 400)
        self.assertEqual(result['Status'], 'UNKNOWN')
        mock_id.assert_called_once()
        mock_start.assert_called_once()

    @patch('lambda_function.start_transcription_job')
    @patch('lambda_function.generate_random_id')
    def test_lambda_handler_exception(self, mock_id, mock_start):
        # Setup mocks
        mock_id.return_value = self.mock_uuid
        mock_start.side_effect = Exception("Test error")

        # Test function
        result = lambda_handler(self.event, self.context)

        # Assertions
        self.assertEqual(result['statusCode'], 400)
        self.assertEqual(result['message'], 'Error processing file')
        self.assertEqual(result['error'], 'Test error')
        mock_id.assert_called_once()
        mock_start.assert_called_once()


if __name__ == '__main__':
    unittest.main()