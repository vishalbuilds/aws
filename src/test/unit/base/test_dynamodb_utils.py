import unittest
from unittest.mock import patch, MagicMock
from strategies.base.dynamodb_utils import DynamoDBUtils

class TestDynamoDBUtils(unittest.TestCase):
    def setUp(self):
        patcher = patch('strategies.base.dynamodb_utils.boto3.resource')
        self.addCleanup(patcher.stop)
        self.mock_resource = patcher.start()
        self.mock_table = MagicMock()
        self.mock_resource.return_value.Table.return_value = self.mock_table
        self.dynamodb_utils = DynamoDBUtils()

    def test_fetch_item_by_key_success(self):
        self.mock_table.get_item.return_value = {'Item': {'id': '1'}}
        result = self.dynamodb_utils.fetch_item_by_key('table', {'id': '1'})
        self.assertEqual(result, {'Item': {'id': '1'}})

    def test_fetch_item_by_key_error(self):
        self.mock_table.get_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.fetch_item_by_key('table', {'id': '1'})

    def test_save_item_success(self):
        self.mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        result = self.dynamodb_utils.save_item('table', {'id': '1'})
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})

    def test_save_item_error(self):
        self.mock_table.put_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.save_item('table', {'id': '1'})

    def test_update_item_attributes_success(self):
        self.mock_table.update_item.return_value = {'Attributes': {'attr': 'val'}}
        result = self.dynamodb_utils.update_item_attributes('table', {'id': '1'}, 'SET attr = :val', {':val': 'val'})
        self.assertEqual(result, {'Attributes': {'attr': 'val'}})

    def test_update_item_attributes_error(self):
        self.mock_table.update_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.update_item_attributes('table', {'id': '1'}, 'SET attr = :val', {':val': 'val'})

    def test_remove_item_by_key_success(self):
        self.mock_table.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        result = self.dynamodb_utils.remove_item_by_key('table', {'id': '1'})
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})

    def test_remove_item_by_key_error(self):
        self.mock_table.delete_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.remove_item_by_key('table', {'id': '1'})

    def test_scan_all_items_with_filter_success(self):
        self.mock_table.scan.return_value = {'Items': [{'id': '1'}]}
        result = self.dynamodb_utils.scan_all_items_with_filter('table')
        self.assertEqual(result, {'Items': [{'id': '1'}]})

    def test_scan_all_items_with_filter_error(self):
        self.mock_table.scan.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.scan_all_items_with_filter('table')

    def test_force_string_success(self):
        self.assertEqual(self.dynamodb_utils.force_string(123), '123')

    def test_force_string_error(self):
        class Bad:
            def __str__(self):
                raise Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.force_string(Bad())

if __name__ == '__main__':
    unittest.main() 