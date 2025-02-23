import boto3
import uuid
import time
import json
import os
from common.logger import Logger  # Importing the logger from a common module

LOGGER=Logger(__name__)

# Environment variables
REGION = os.environ.get('AWS_REGION','us-east-1')
TARGET_OUTPUT_BUCKET=os.environ.get("TARGET_OUTPUT_BUCKET",'new-recording-with-pii')


# Initialize the transcribe client
transcribe_client = boto3.client('transcribe',region_name=REGION)



# Function to generate a random ID
def generate_random_id():
    return str(uuid.uuid4())

# Function to start the transcription job
def start_transcription_job(transcription_job_name,source_input_bucket, target_output_bucket):
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
    try:
        response = transcribe_client.get_transcription_job(TranscriptionJobName=transcription_job_name)
        return response
    except Exception as e:
        LOGGER.error(f"Error retrieving transcription job status: {e}")
        raise

# Function to check the transcription job status
def check_transcription_status(transcription_job_name):
    while True:
        status, response = get_transcription_job_status(transcription_job_name)
        LOGGER.info(f"Transcription job status: {status}")
        if status in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    if status == 'COMPLETED':
        transcript_file_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        LOGGER.info(f"Transcription completed. Result stored in: {target_output_bucket}, File URI: {transcript_file_uri}")
        return transcript_file_uri
    else:
        LOGGER.error(f"Transcription job failed: {json.dumps(status)}")
        raise Exception("Transcription job failed")

# Lambda handler function
def lambda_handler(event, context):
    LOGGER.info(f" Starting LambdaFunctionName: { context.function_name}, Region: {REGION}")

    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    media_file_uri = f"s3://{source_bucket}/{source_key}"

    transcription_job_name = f"Transcription_Job_Name-{generate_random_id()}"



    try:
        transcription_job_name = start_transcription_job(source_bucket, source_key, target_output_bucket)
        transcript_file_uri = check_transcription_status(transcription_job_name, target_output_bucket)
    except Exception as e:
        LOGGER.error(f"Error processing file {source_key} in Lambda function {lambda_function_name}: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Error processing file', 'error': str(e), 'file_name': source_key,})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(
            {'message': 'File processed and transcription result stored successfully', 'file_name': source_key,})
    }
