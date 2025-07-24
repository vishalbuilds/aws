import boto3
from common.logger import Logger

class DynamoDBClient:
    def __init__(self, region_name=None):
        self.logger = Logger(__name__)
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)

    def get_item(self, table_name, key):
        self.logger.info(f"Getting item from table: {table_name}, key: {key}")
        table = self.dynamodb.Table(table_name)
        return table.get_item(Key=key)

    def put_item(self, table_name, item):
        self.logger.info(f"Putting item to table: {table_name}, item: {item}")
        table = self.dynamodb.Table(table_name)
        return table.put_item(Item=item)

    # Add more methods as needed 