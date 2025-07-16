import unittest
from unittest.mock import patch, MagicMock
from strategies.base.transcribe_utils import TranscribeUtils

class TestTranscribeUtils(unittest.TestCase):
    def setUp(self):
        patcher = patch('boto3.client')
        self.addCleanup(patcher.stop)
        self.mock_client = patcher.start()
        self.mock_transcribe = MagicMock()
        self.mock_client.return_value = self.mock_transcribe
        self.transcribe_utils = TranscribeUtils(region_name='us-east-1')

    def test_start_transcription_job(self):
        self.mock_transcribe.start_transcription_job.return_value = {'TranscriptionJob': {'TranscriptionJobStatus': 'IN_PROGRESS'}}
        result = self.transcribe_utils.start_transcription_job('job', 'uri', 'bucket')
        self.assertEqual(result, {'TranscriptionJob': {'TranscriptionJobStatus': 'IN_PROGRESS'}})

    def test_get_transcription_job(self):
        self.mock_transcribe.get_transcription_job.return_value = {'TranscriptionJob': {'TranscriptionJobStatus': 'COMPLETED'}}
        result = self.transcribe_utils.get_transcription_job('job')
        self.assertEqual(result, {'TranscriptionJob': {'TranscriptionJobStatus': 'COMPLETED'}})

    def test_check_transcription_status(self):
        self.mock_transcribe.get_transcription_job.side_effect = [
            {'TranscriptionJob': {'TranscriptionJobStatus': 'IN_PROGRESS'}},
            {'TranscriptionJob': {'TranscriptionJobStatus': 'COMPLETED'}}
        ]
        status = self.transcribe_utils.check_transcription_status('job')
        self.assertEqual(status, 'COMPLETED')

if __name__ == '__main__':
    unittest.main() 