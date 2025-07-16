"""
DynamoDBUtils: A comprehensive utility class for DynamoDB CRUD and batch operations.

This class provides high-level, descriptive methods for common and advanced DynamoDB operations,
including single and batch CRUD, attribute-based queries, existence checks, and more.
All methods include logging and error handling for robust production use.
"""
from client.dynamodb_client import DynamoDBClient
from common.logger import Logger
import os

class DynamoDBUtils(DynamoDBClient):
    """
    Utility class for DynamoDB operations with descriptive, robust methods.
    Inherits from DynamoDBClient and adds logging, error handling, and high-level helpers.
    """
    def __init__(self):
        """
        Initialize the DynamoDBUtils class with region and logger.
        """
        super().__init__(region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        self.logger = Logger(__name__)

    def fetch_item_by_key(self, table_name, key):
        """
        Fetch a single item from a DynamoDB table by its key.
        Args:
            table_name (str): The name of the DynamoDB table.
            key (dict): The primary key of the item to fetch.
        Returns:
            dict: The response from DynamoDB get_item.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Fetching item from {table_name} with key {key}")
        try:
            return self.get_item(table_name, key)
        except Exception as e:
            self.logger.error(f"Error fetching item: {e}")
            raise

    def save_item(self, table_name, item, condition_expression=None, expression_values=None):
        """
        Save (put) an item into a DynamoDB table. Optionally use a condition expression.
        Args:
            table_name (str): The name of the DynamoDB table.
            item (dict): The item to save.
            condition_expression (str, optional): Condition for the put operation.
            expression_values (dict, optional): Values for the condition expression.
        Returns:
            dict: The response from DynamoDB put_item.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Saving item in {table_name}: {item}")
        table = self.dynamodb.Table(table_name)
        kwargs = {'Item': item}
        if condition_expression and expression_values:
            kwargs['ConditionExpression'] = condition_expression
            kwargs['ExpressionAttributeValues'] = expression_values
        try:
            return table.put_item(**kwargs)
        except Exception as e:
            self.logger.error(f"Error saving item: {e}")
            raise

    def update_item_attributes(self, table_name, key, update_expression, expression_values, condition_expression=None):
        """
        Update attributes of a single item in a DynamoDB table.
        Args:
            table_name (str): The name of the DynamoDB table.
            key (dict): The primary key of the item to update.
            update_expression (str): The update expression (e.g., 'SET attr = :val').
            expression_values (dict): Values for the update expression.
            condition_expression (str, optional): Condition for the update operation.
        Returns:
            dict: The response from DynamoDB update_item.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Updating item in {table_name} with key {key}")
        table = self.dynamodb.Table(table_name)
        kwargs = {
            'Key': key,
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': "UPDATED_NEW"
        }
        if condition_expression:
            kwargs['ConditionExpression'] = condition_expression
        try:
            return table.update_item(**kwargs)
        except Exception as e:
            self.logger.error(f"Error updating item: {e}")
            raise

    def remove_item_by_key(self, table_name, key, condition_expression=None, expression_values=None):
        """
        Remove (delete) a single item from a DynamoDB table by its key.
        Args:
            table_name (str): The name of the DynamoDB table.
            key (dict): The primary key of the item to delete.
            condition_expression (str, optional): Condition for the delete operation.
            expression_values (dict, optional): Values for the condition expression.
        Returns:
            dict: The response from DynamoDB delete_item.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Removing item from {table_name} with key {key}")
        table = self.dynamodb.Table(table_name)
        kwargs = {'Key': key}
        if condition_expression and expression_values:
            kwargs['ConditionExpression'] = condition_expression
            kwargs['ExpressionAttributeValues'] = expression_values
        try:
            return table.delete_item(**kwargs)
        except Exception as e:
            self.logger.error(f"Error removing item: {e}")
            raise

    def fetch_multiple_items_by_keys(self, table_name, keys):
        """
        Fetch multiple items from a DynamoDB table by a list of keys (batch get).
        Args:
            table_name (str): The name of the DynamoDB table.
            keys (list): List of key dicts for the items to fetch.
        Returns:
            dict: The response from DynamoDB batch_get_item.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Fetching multiple items from {table_name} with keys {keys}")
        try:
            return self.dynamodb.batch_get_item(RequestItems={table_name: {'Keys': keys}})
        except Exception as e:
            self.logger.error(f"Error fetching multiple items: {e}")
            raise

    def bulk_save_or_remove_items(self, table_name, put_items=None, delete_keys=None):
        """
        Bulk save (put) or remove (delete) multiple items in a DynamoDB table.
        Args:
            table_name (str): The name of the DynamoDB table.
            put_items (list, optional): List of items to put.
            delete_keys (list, optional): List of key dicts for items to delete.
        Returns:
            None
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Bulk saving or removing items in {table_name}")
        try:
            with self.dynamodb.Table(table_name).batch_writer() as batch:
                if put_items:
                    for item in put_items:
                        batch.put_item(Item=item)
                if delete_keys:
                    for key in delete_keys:
                        batch.delete_item(Key=key)
        except Exception as e:
            self.logger.error(f"Error in bulk save or remove: {e}")
            raise

    def find_items_by_key_condition(self, table_name, key_condition_expression, expression_values, index_name=None, filter_expression=None):
        """
        Query items in a DynamoDB table using a key condition expression.
        Args:
            table_name (str): The name of the DynamoDB table.
            key_condition_expression: The key condition expression (boto3 condition object).
            expression_values (dict): Values for the key condition expression.
            index_name (str, optional): Name of the index to query.
            filter_expression: Additional filter expression (boto3 condition object).
        Returns:
            dict: The response from DynamoDB query.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Finding items in {table_name} with key condition {key_condition_expression}")
        table = self.dynamodb.Table(table_name)
        kwargs = {
            'KeyConditionExpression': key_condition_expression,
            'ExpressionAttributeValues': expression_values
        }
        if index_name:
            kwargs['IndexName'] = index_name
        if filter_expression:
            kwargs['FilterExpression'] = filter_expression
        try:
            return table.query(**kwargs)
        except Exception as e:
            self.logger.error(f"Error finding items: {e}")
            raise

    def scan_all_items_with_filter(self, table_name, filter_expression=None, expression_values=None):
        """
        Scan all items in a DynamoDB table, optionally with a filter expression.
        Args:
            table_name (str): The name of the DynamoDB table.
            filter_expression: Filter expression (boto3 condition object), optional.
            expression_values (dict, optional): Values for the filter expression.
        Returns:
            dict: The response from DynamoDB scan.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Scanning all items in {table_name}")
        table = self.dynamodb.Table(table_name)
        kwargs = {}
        if filter_expression:
            kwargs['FilterExpression'] = filter_expression
        if expression_values:
            kwargs['ExpressionAttributeValues'] = expression_values
        try:
            return table.scan(**kwargs)
        except Exception as e:
            self.logger.error(f"Error scanning items: {e}")
            raise

    def fetch_items_by_attribute(self, table_name, attribute_name, attribute_value):
        """
        Fetch all items from a DynamoDB table where a given attribute matches a value.
        Args:
            table_name (str): The name of the DynamoDB table.
            attribute_name (str): The attribute to filter by.
            attribute_value: The value to match.
        Returns:
            dict: The response from DynamoDB scan.
        Raises:
            Exception: If the operation fails.
        """
        self.logger.info(f"Fetching items from {table_name} where {attribute_name} = {attribute_value}")
        table = self.dynamodb.Table(table_name)
        from boto3.dynamodb.conditions import Attr
        try:
            return table.scan(FilterExpression=Attr(attribute_name).eq(attribute_value))
        except Exception as e:
            self.logger.error(f"Error fetching items by attribute: {e}")
            raise

    def update_items_by_attribute(self, table_name, attribute_name, attribute_value, update_expression, expression_values):
        """
        Update all items in a DynamoDB table where a given attribute matches a value.
        Args:
            table_name (str): The name of the DynamoDB table.
            attribute_name (str): The attribute to filter by.
            attribute_value: The value to match.
            update_expression (str): The update expression.
            expression_values (dict): Values for the update expression.
        Returns:
            list: List of responses from DynamoDB update_item.
        """
        self.logger.info(f"Updating items in {table_name} where {attribute_name} = {attribute_value}")
        items = self.fetch_items_by_attribute(table_name, attribute_name, attribute_value).get('Items', [])
        results = []
        for item in items:
            key = {k: item[k] for k in item if k in expression_values}
            try:
                result = self.update_item_attributes(table_name, key, update_expression, expression_values)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error updating item {key}: {e}")
        return results

    def remove_items_by_attribute(self, table_name, attribute_name, attribute_value):
        """
        Remove all items from a DynamoDB table where a given attribute matches a value.
        Args:
            table_name (str): The name of the DynamoDB table.
            attribute_name (str): The attribute to filter by.
            attribute_value: The value to match.
        Returns:
            list: List of responses from DynamoDB delete_item.
        """
        self.logger.info(f"Removing items from {table_name} where {attribute_name} = {attribute_value}")
        items = self.fetch_items_by_attribute(table_name, attribute_name, attribute_value).get('Items', [])
        results = []
        for item in items:
            key = {attribute_name: item[attribute_name]}
            try:
                result = self.remove_item_by_key(table_name, key)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error removing item {key}: {e}")
        return results

    def item_exists(self, table_name, key):
        """
        Check if an item exists in a DynamoDB table by its key.
        Args:
            table_name (str): The name of the DynamoDB table.
            key (dict): The primary key of the item to check.
        Returns:
            bool: True if the item exists, False otherwise.
        """
        self.logger.info(f"Checking if item exists in {table_name} with key {key}")
        try:
            response = self.fetch_item_by_key(table_name, key)
            return 'Item' in response and response['Item'] is not None
        except Exception as e:
            self.logger.error(f"Error checking item existence: {e}")
            return False

    def count_items_by_condition(self, table_name, condition_expression, expression_values):
        """
        Count the number of items in a DynamoDB table matching a condition.
        Args:
            table_name (str): The name of the DynamoDB table.
            condition_expression: The filter expression (boto3 condition object).
            expression_values (dict): Values for the filter expression.
        Returns:
            int: The count of matching items.
        """
        self.logger.info(f"Counting items in {table_name} by condition")
        table = self.dynamodb.Table(table_name)
        try:
            response = table.scan(
                FilterExpression=condition_expression,
                ExpressionAttributeValues=expression_values,
                Select='COUNT'
            )
            return response.get('Count', 0)
        except Exception as e:
            self.logger.error(f"Error counting items: {e}")
            return 0

    def force_string(self, value):
        """
        Convert any value to a string, with logging and error handling.
        Args:
            value: The value to convert.
        Returns:
            str: The value as a string.
        Raises:
            Exception: If conversion fails.
        """
        self.logger.info(f"Forcing value to string: {value}")
        try:
            return str(value)
        except Exception as e:
            self.logger.error(f"Error forcing value to string: {e}")
            raise 