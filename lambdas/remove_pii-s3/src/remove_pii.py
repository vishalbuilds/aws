import uuid
import time
import os
import boto3



from common.logger import Logger
LOGGER = Logger(__name__)

# Environment variables
REGION = os.environ.get('AWS_REGION','us-east-1')
TARGET_OUTPUT_BUCKET=os.environ.get("TARGET_OUTPUT_BUCKET",'new-recording-with-pii')


# Initialize the transcribe client
transcribe_client = boto3.client('transcribe',region_name=REGION)


# Function to generate a random ID
def generate_random_id():
    LOGGER.info('Generating random ID')
    try:
        return str(uuid.uuid4())
    except Exception as e:
        LOGGER.error(f"Error generating random ID: {e}")
        raise e

# Function to start the transcription job
def start_transcription_job(transcription_job_name,source_input_bucket, target_output_bucket):
    LOGGER.info('Start the transcription job')
    LOGGER.info(f"Processing file: {transcription_job_name} from bucket: {source_input_bucket}")

    try:
        response=transcribe_client.start_transcription_job(
            TranscriptionJobName=transcription_job_name,
            LanguageCode='en-US',
            Media={'MediaFileUri': source_input_bucket},
            ContentRedaction={'RedactionType': 'PII', 'RedactionOutput': 'redacted'},
            OutputBucketName=target_output_bucket,
        )
        return response
    except Exception as e:
        LOGGER.error(f"Error starting transcription job: {e}")
        raise

# Function to get the transcription job status
def get_transcription_job_status(transcription_job_name):
    LOGGER.info('Get the transcription job status')
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=transcription_job_name
            )
        return response
    except Exception as e:
        LOGGER.error(f"Error retrieving transcription job status: {e}")
        raise

# Function to check the transcription job status
def check_transcription_status(transcription_job_name):
    LOGGER.info('Check the transcription job status')
    try:
        LOGGER.info(f"Checking transcription job status for: {transcription_job_name}")
        while True:
            response = get_transcription_job_status(transcription_job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            LOGGER.info(f"Transcription job status: {status}")
            if status =='COMPLETED':
                LOGGER.info(f"Transcription job completed with status: {status}")
                return status
            elif status == 'IN_PROGRESS':
                LOGGER.info("Transcription job in progress...")
                time.sleep(5)
            elif status == 'FAILED':
                LOGGER.error(f"Transcription job failed: {status}")
                return status
            else:
                LOGGER.error(f"Transcription job status not found:{response}")
                return "UNKNOWN"
    except Exception as e:
        LOGGER.error(f"Error checking transcription job status: {e}")
        raise e


# Lambda handler function
def lambda_handler(event, context):
    LOGGER.info('Lambda handler function')
    LOGGER.info(f" Starting LambdaFunctionName:redact-pii, Region: {REGION}")
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    media_file_uri = f"s3://{source_bucket}/{source_key}"
    transcription_job_name = f"Transcription_Job_Name-{generate_random_id()}"
    try:
        transcription_start=start_transcription_job(transcription_job_name, media_file_uri, TARGET_OUTPUT_BUCKET)
        transcription_start_status=transcription_start['TranscriptionJob']['TranscriptionJobStatus']
        if transcription_start_status in ['IN_PROGRESS','QUEUED']:
            time.sleep(5)
            check_status=check_transcription_status(transcription_job_name)
            LOGGER.info(f"Transcription job processing completed with status: {check_status}")
            return {
                'statusCode': 200,
                'message': 'Transcription job processing completed',
                'media_file_uri': f"s3://{source_bucket}/{source_key}",
                'Status': check_status
                }
        elif transcription_start_status in ['COMPLETED']:
            LOGGER.error(f"Transcription job processing completed with status: {transcription_start_status}")
            return {
                'statusCode': 200,
                'message': 'Transcription job processing completed',
                'media_file_uri': f"s3://{source_bucket}/{source_key}",
                'Status': transcription_start_status
            }
        elif transcription_start_status in ['FAILED']:
            LOGGER.error(f"Transcription job processing failed with status: {transcription_start_status}")
            return {
                'statusCode': 400,
                'message': 'Transcription job processing failed',
                'media_file_uri': f"s3://{source_bucket}/{source_key}",
                'Status': transcription_start_status
            }
        else:
            LOGGER.error("Transcription job processing not found with status")
            return {
                'statusCode': 400,
                'message': 'Transcription job processing not found',
                'media_file_uri': f"s3://{source_bucket}/{source_key}",
                'Status': 'UNKNOWN'
            }
    except Exception as e:
        LOGGER.error(f"Error processing file {media_file_uri}, Error: {e}")
        return {
            'statusCode': 400,
            'message': 'Error processing file',
            'error': str(e),
            'media_file_uri': f"s3://{source_bucket}/{source_key}",
        }