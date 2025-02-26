import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

#from aws.lambda.s3.remove_pii.src import remove_pii
from aws.lambda.s3.remove_pii.src.remove_pii import generate_random_id



patch.dict(os.environ, {'REGION': 'us-east-1', 'TARGET_OUTPUT_BUCKET': 'target-bucket'}).start()

class TestRemovePII(unittest.TestCase):
    @patch.dict(os.environ, {'REGION': 'us-east-1', 'TARGET_OUTPUT_BUCKET': 'target-bucket'})
    @patch('remove_pii.generate_random_id')  # Use correct patch path
    def test_generate_random_id(self, mock_generate_random_id):
        mock_generate_random_id.return_value = '1234'
        self.assertEqual(generate_random_id(), '1234')

if __name__ == "__main__":
    unittest.main()