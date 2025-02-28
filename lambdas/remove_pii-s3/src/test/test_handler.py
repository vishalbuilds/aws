import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure the module is correctly imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.remove_pii import (
    generate_random_id,
    start_transcription_job,
    get_transcription_job_status,
    check_transcription_status,
    lambda_handler
)

class TestRemovePII(unittest.TestCase):
    @patch('uuid.uuid4')
    def test_generate_random_id_success(self, mock_uuid):
        """Test case for generate_random_id function success"""
        mock_uuid.return_value = 'abcde123-4567-89ab-cdef-0123456789ab'
        random_id = generate_random_id()
        self.assertEqual(random_id, 'abcde123-4567-89ab-cdef-0123456789ab')

    @patch('uuid.uuid4')
    def test_generate_random_id_failure(self, mock_uuid):
        """Test case for generate_random_id function failure"""
        mock_uuid.side_effect = Exception('Error generating random id')
        with self.assertRaises(Exception) as context:
            generate_random_id()
        self.assertEqual(str(context.exception), "Error generating random id")

    @patch('src.remove_pii.transcribe_client')
    def test_start_transcription_job_success(self, mock_transcribe_client):
        """Test case for start_transcription_job function success"""
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'IN_PROGRESS'}}
        mock_transcribe_client.start_transcription_job.return_value = expected_response
        response = start_transcription_job('test-job', 's3://source-bucket/test.mp3', 'target-bucket')
        self.assertEqual(response, expected_response)

    @patch('src.remove_pii.transcribe_client')
    def test_start_transcription_job_failure(self, mock_transcribe_client):
        """Test case for start_transcription_job function failure"""
        expected_response_failure = 'Transcription job failed'
        mock_transcribe_client.start_transcription_job.side_effect = Exception(expected_response_failure)
        with self.assertRaises(Exception) as context:
            start_transcription_job('test-job', 's3://source-bucket/test.mp3', 'target-bucket')
        self.assertEqual(str(context.exception), expected_response_failure)

    @patch('src.remove_pii.transcribe_client')
    def test_get_transcription_job_status_success(self, mock_transcribe_client):
        """Test case for get_transcription_job_status function success"""
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'IN_PROGRESS'}}
        mock_transcribe_client.get_transcription_job.return_value = expected_response
        result = get_transcription_job_status('test-job')
        self.assertEqual(result, expected_response)

    @patch('src.remove_pii.transcribe_client')
    def test_get_transcription_job_status_failure(self, mock_transcribe_client):
        """Test case for get_transcription_job_status function failure"""
        expected_response_failure = 'Transcription job failed'
        mock_transcribe_client.get_transcription_job.side_effect = Exception(expected_response_failure)
        with self.assertRaises(Exception) as context:
            get_transcription_job_status('test-job')
        self.assertEqual(str(context.exception), expected_response_failure)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestRemovePII))
