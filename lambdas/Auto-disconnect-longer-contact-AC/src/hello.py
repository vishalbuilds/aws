import json
import os
from datetime import datetime, timezone
import boto3
from common.logger import Logger

# Initialize the custom logger
LOGGER = Logger(__name__)

ACTIVE_TIME= os.getenv('ACTIVE_TIM',5)
UPDATE_TIME=os.getenv('UPDATE_TIME',2)

INSTANCE=os.getenv('INSTANCE')
REGION=os.getenv('REGION','us-east-1')

Connect=boto3.client('connect',region_name=REGION)

