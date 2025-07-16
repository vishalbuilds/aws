import unittest
from unittest.mock import patch, MagicMock
from strategies.base.s3_utils import S3Utils

class TestS3Utils(unittest.TestCase):
    def setUp(self):
        patcher = patch('boto3.client')
        self.addCleanup(patcher.stop)
        self.mock_client = patcher.start()
        self.mock_s3 = MagicMock()
        self.mock_client.return_value = self.mock_s3
        self.s3_utils = S3Utils(region_name='us-east-1')

    def test_get_object(self):
        self.mock_s3.get_object.return_value = {'Body': b'data'}
        result = self.s3_utils.get_object('bucket', 'key')
        self.assertEqual(result, {'Body': b'data'})

    def test_put_object(self):
        self.mock_s3.put_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        result = self.s3_utils.put_object('bucket', 'key', b'data')
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})

    def test_delete_object(self):
        self.mock_s3.delete_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 204}}
        result = self.s3_utils.delete_object('bucket', 'key')
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 204}})

    def test_list_objects(self):
        self.mock_s3.list_objects_v2.return_value = {'Contents': []}
        result = self.s3_utils.list_objects('bucket')
        self.assertEqual(result, {'Contents': []})

if __name__ == '__main__':
    unittest.main() 