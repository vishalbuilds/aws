import unittest
from strategies.base.s3_utils import S3Utils

class TestS3Utils(unittest.TestCase):
    def setUp(self):
        self.s3_utils = S3Utils(region_name='us-east-1')

    def test_get_object(self):
        self.assertTrue(hasattr(self.s3_utils, 'get_object'))

    def test_put_object(self):
        self.assertTrue(hasattr(self.s3_utils, 'put_object'))

    def test_delete_object(self):
        self.assertTrue(hasattr(self.s3_utils, 'delete_object'))

    def test_list_objects(self):
        self.assertTrue(hasattr(self.s3_utils, 'list_objects'))

if __name__ == '__main__':
    unittest.main() 