import unittest
from strategies.base.transcribe_utils import TranscribeUtils

class TestTranscribeUtils(unittest.TestCase):
    def setUp(self):
        self.transcribe_utils = TranscribeUtils(region_name='us-east-1')

    def test_start_transcription_job(self):
        # This is a placeholder. Use mocks for AWS calls in real tests.
        self.assertTrue(hasattr(self.transcribe_utils, 'start_transcription_job'))

    def test_get_transcription_job(self):
        self.assertTrue(hasattr(self.transcribe_utils, 'get_transcription_job'))

    def test_check_transcription_status(self):
        self.assertTrue(hasattr(self.transcribe_utils, 'check_transcription_status'))

if __name__ == '__main__':
    unittest.main() 