from common.logger import Logger  

# Initialize the custom logger
logger = Logger()
LOGGER = Logger(__name__)

def lambda_handler(event, context):
    try:
        logger.info("Lambda function invoked")
        return {
            "statusCode": 200,
            "body": "Hello Vishal Singh, this is your sample file."
        }
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return {
            "statusCode": 500,
            "body": "An error occurred while processing the request."
        }