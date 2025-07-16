import unittest
from unittest.mock import patch, MagicMock
from strategies.base.dynamodb_utils import DynamoDBUtils

class TestDynamoDBUtils(unittest.TestCase):
    def setUp(self):
        self.dynamodb_utils = DynamoDBUtils()

    @patch('strategies.base.dynamodb_utils.DynamoDBUtils.get_item')
    def test_fetch_item_by_key_success(self, mock_get_item):
        mock_get_item.return_value = {'Item': {'id': '1'}}
        result = self.dynamodb_utils.fetch_item_by_key('table', {'id': '1'})
        self.assertEqual(result, {'Item': {'id': '1'}})

    @patch('strategies.base.dynamodb_utils.DynamoDBUtils.get_item', side_effect=Exception('fail'))
    def test_fetch_item_by_key_error(self, mock_get_item):
        with self.assertRaises(Exception):
            self.dynamodb_utils.fetch_item_by_key('table', {'id': '1'})

    @patch('boto3.resource')
    def test_save_item_success(self, mock_resource):
        table = MagicMock()
        table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_resource.return_value.Table.return_value = table
        result = self.dynamodb_utils.save_item('table', {'id': '1'})
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})

    @patch('boto3.resource')
    def test_save_item_error(self, mock_resource):
        table = MagicMock()
        table.put_item.side_effect = Exception('fail')
        mock_resource.return_value.Table.return_value = table
        with self.assertRaises(Exception):
            self.dynamodb_utils.save_item('table', {'id': '1'})

    @patch('boto3.resource')
    def test_update_item_attributes_success(self, mock_resource):
        table = MagicMock()
        table.update_item.return_value = {'Attributes': {'attr': 'val'}}
        mock_resource.return_value.Table.return_value = table
        result = self.dynamodb_utils.update_item_attributes('table', {'id': '1'}, 'SET attr = :val', {':val': 'val'})
        self.assertEqual(result, {'Attributes': {'attr': 'val'}})

    @patch('boto3.resource')
    def test_update_item_attributes_error(self, mock_resource):
        table = MagicMock()
        table.update_item.side_effect = Exception('fail')
        mock_resource.return_value.Table.return_value = table
        with self.assertRaises(Exception):
            self.dynamodb_utils.update_item_attributes('table', {'id': '1'}, 'SET attr = :val', {':val': 'val'})

    @patch('boto3.resource')
    def test_remove_item_by_key_success(self, mock_resource):
        table = MagicMock()
        table.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_resource.return_value.Table.return_value = table
        result = self.dynamodb_utils.remove_item_by_key('table', {'id': '1'})
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})

    @patch('boto3.resource')
    def test_remove_item_by_key_error(self, mock_resource):
        table = MagicMock()
        table.delete_item.side_effect = Exception('fail')
        mock_resource.return_value.Table.return_value = table
        with self.assertRaises(Exception):
            self.dynamodb_utils.remove_item_by_key('table', {'id': '1'})

    @patch('boto3.resource')
    def test_scan_all_items_with_filter_success(self, mock_resource):
        table = MagicMock()
        table.scan.return_value = {'Items': [{'id': '1'}]}
        mock_resource.return_value.Table.return_value = table
        result = self.dynamodb_utils.scan_all_items_with_filter('table')
        self.assertEqual(result, {'Items': [{'id': '1'}]})

    @patch('boto3.resource')
    def test_scan_all_items_with_filter_error(self, mock_resource):
        table = MagicMock()
        table.scan.side_effect = Exception('fail')
        mock_resource.return_value.Table.return_value = table
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