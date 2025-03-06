import unittest
from unittest.mock import patch
import os
import sys

# Ensure the module is correctly imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import remove_pii as handler




class TestRemovePII(unittest.TestCase):

    #Test case for generate_random_id function success
    @patch('uuid.uuid4')
    def test_generate_random_id_success(self, mock_uuid):
        mock_uuid.return_value = 'abcde123-4567-89ab-cdef-0123456789ab'
        random_id = handler.generate_random_id()
        self.assertEqual(random_id, 'abcde123-4567-89ab-cdef-0123456789ab')

    #Test case for generate_random_id function failure
    @patch('uuid.uuid4')
    def test_generate_random_id_failure(self, mock_uuid):
        mock_uuid.side_effect = Exception('Error generating random id')
        with self.assertRaises(Exception) as context:
            handler.generate_random_id()
        self.assertEqual(str(context.exception), "Error generating random id")

    #Test case for start_transcription_job function success
    @patch('src.remove_pii.transcribe_client')
    def test_start_transcription_job_success(self, mock_transcribe_client):
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'IN_PROGRESS'}}
        mock_transcribe_client.start_transcription_job.return_value = expected_response
        response = handler.start_transcription_job('test-job', 's3://source-bucket/test.mp3', 'target-bucket')
        self.assertEqual(response, expected_response)

    #Test case for start_transcription_job function failure
    @patch('src.remove_pii.transcribe_client')
    def test_start_transcription_job_failure(self, mock_transcribe_client):
        expected_response_failure = 'Transcription job failed'
        mock_transcribe_client.start_transcription_job.side_effect = Exception(expected_response_failure)
        with self.assertRaises(Exception) as context:
            handler.start_transcription_job('test-job', 's3://source-bucket/test.mp3', 'target-bucket')
        self.assertEqual(str(context.exception), expected_response_failure)

    #Test case for get_transcription_job_status function success
    @patch('src.remove_pii.transcribe_client')
    def test_get_transcription_job_status_success(self, mock_transcribe_client):
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'IN_PROGRESS'}}
        mock_transcribe_client.get_transcription_job.return_value = expected_response
        result = handler.get_transcription_job_status('test-job')
        self.assertEqual(result, expected_response)

    #Test case for get_transcription_job_status function failure
    @patch('src.remove_pii.transcribe_client')
    def test_get_transcription_job_status_failure(self, mock_transcribe_client):
        expected_response_failure = 'Transcription job failed'
        mock_transcribe_client.get_transcription_job.side_effect = Exception(expected_response_failure)
        with self.assertRaises(Exception) as context:
            handler.get_transcription_job_status('test-job')
        self.assertEqual(str(context.exception), expected_response_failure)

    #Test case for check_transcription_status function success
    @patch('src.remove_pii.transcribe_client')
    def test_check_transcription_status_success(self, mock_transcribe_client):
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'COMPLETED'}}
        mock_transcribe_client.get_transcription_job.return_value = expected_response
        result = handler.check_transcription_status('test-job')
        self.assertEqual(result, 'COMPLETED')

    #Test case for check_transcription_status function failed
    @patch('src.remove_pii.transcribe_client')
    def test_check_transcription_status_failed(self, mock_transcribe_client):
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'FAILED'}}
        mock_transcribe_client.get_transcription_job.return_value = expected_response
        result = handler.check_transcription_status('test-job')
        self.assertEqual(result, 'FAILED')

    #Test case for check_transcription_status function unknown
    @patch('src.remove_pii.transcribe_client')
    def test_check_transcription_status_unknown(self, mock_transcribe_client):
        expected_response = {'TranscriptionJob': {'TranscriptionJobName': 'test-job','TranscriptionJobStatus': ''}}
        mock_transcribe_client.get_transcription_job.return_value = expected_response
        result = handler.check_transcription_status('test-job')
        self.assertEqual(result, 'UNKNOWN')

    #Test case for check_transcription_status function when it transitions from IN_PROGRESS to COMPLETED
    @patch('src.remove_pii.get_transcription_job_status')
    @patch('time.sleep', return_value=None)
    def test_check_transcription_status_in_progress_to_completed(self, mock_sleep, mock_get_transcription_job_status):
        expected_response = [
            {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'IN_PROGRESS'}},
            {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'IN_PROGRESS'}},
            {'TranscriptionJob': {'TranscriptionJobName': 'test-job', 'TranscriptionJobStatus': 'COMPLETED'}}
        ]
        mock_get_transcription_job_status.side_effect = lambda job_name: expected_response.pop(0)
        result = handler.check_transcription_status('test-job')
        self.assertEqual(result, 'COMPLETED')

    #Test case for check_transcription_status function failure
    @patch('src.remove_pii.transcribe_client')
    def test_check_transcription_status_failure(self,mock_transcribe_client):
        expected_response_failure = 'Transcription job failed'
        mock_transcribe_client.get_transcription_job.side_effect = Exception(expected_response_failure)
        with self.assertRaises(Exception) as context:
            handler.check_transcription_status('test-job')
        self.assertEqual(str(context.exception), expected_response_failure)

    #test case for lambda handler function in progress to complete
    @patch('src.remove_pii.transcribe_client')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_in_progress_to_complete(self,mock_sleep,moc_transcribe_client):
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "test-file.mp3"}
                }
            }]
        }
        context={}
        moc_transcribe_client.start_transcription_job.return_value={"TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}}
        moc_transcribe_client.get_transcription_job.return_value = {"TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}}
        moc_transcribe_client.check_transcription_status.return_value='COMPLETED'
        response=handler.lambda_handler(event, context)
        self.assertEqual(response["Status"], "COMPLETED")

    #test case for lambda handler function complete
    @patch('src.remove_pii.transcribe_client')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_complete(self,mock_sleep,moc_transcribe_client):
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "test-file.mp3"}
                }
            }]
        }
        context={}
        moc_transcribe_client.start_transcription_job.return_value={"TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}}
        response=handler.lambda_handler(event, context)
        self.assertEqual(response["Status"], "COMPLETED")

    # test case for lambda handler function failed
    @patch('src.remove_pii.transcribe_client')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_failed(self, mock_sleep, moc_transcribe_client):
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "test-file.mp3"}
                }
            }]
        }
        context = {}
        moc_transcribe_client.start_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "FAILED"}}
        response = handler.lambda_handler(event, context)
        self.assertEqual(response["Status"], "FAILED")

    # test case for lambda handler function failed
    @patch('src.remove_pii.transcribe_client')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_failed(self, mock_sleep, moc_transcribe_client):
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "test-file.mp3"}
                }
            }]
        }
        context = {}
        moc_transcribe_client.start_transcription_job.return_value = {"TranscriptionJob": {"TranscriptionJobStatus": "---"}}
        response = handler.lambda_handler(event, context)
        self.assertEqual(response["Status"], "UNKNOWN")

    # test case for lambda handler function exception
    @patch('src.remove_pii.start_transcription_job')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_failed(self, mock_sleep, moc_start_transcription_job):
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "test-file.mp3"}
                }
            }]
        }
        context_test = {}
        expected_response_failure = 'Transcription job failed'
        moc_start_transcription_job.side_effect=Exception(expected_response_failure)
        response = handler.lambda_handler(event, context_test)
        self.assertEqual(response['error'], expected_response_failure)



if __name__ == '__main__':
    unittest.main()
