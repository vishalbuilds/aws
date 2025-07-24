import boto3
from src.common.logger import Logger

class ConnectClient:
    def __init__(self, region_name=None):
        self.logger = Logger(__name__)
        self.connect = boto3.client('connect', region_name=region_name)
