import boto3
from common.logger import Logger

class ConnectClient:
    def __init__(self, region_name=None):
        self.logger = Logger(__name__)
        self.connect = boto3.client('connect', region_name=region_name)

    def start_outbound_voice_contact(self, **kwargs):
        self.logger.info(f"Starting outbound voice contact with params: {kwargs}")
        return self.connect.start_outbound_voice_contact(**kwargs)

    # Add more methods as needed 