
#Lambda function to redact pii information.
import boto3
import uuid
import time
import json
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_random_id():
    return str(uuid.uuid4())

transcribe = boto3.client('transcribe')

def lambda_handler(event,context):

    source_bucket= event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
                                                     
    target_output_bucket="new-recording-with-pii"

    lambda_function_name=os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
    aws_region=os.environ.get('AWS_REGION')
    logger.info(f"LambdaFunctionName: {lambda_function_name}, Region: {aws_region}")


    job_id= generate_random_id()

    Transcription_Job_Name=f"Transcription_Job_Name-{job_id}"
    Media_File_Uri=f"s3://{source_bucket}/{source_key}"
    logger.info (f"Initiating Redacting PII on file: {source_key} from bucket: {source_bucket}")
    

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=Transcription_Job_Name,
            LanguageCode='en-US',
            Media={'MediaFileUri': Media_File_Uri},
            ContentRedaction={'RedactionType': 'PII',
                              'RedactionOutput': 'redacted'},
            OutputBucketName=target_output_bucket,
            )
        logger.info (f"Running transcribe job: {Transcription_Job_Name}")
        
        while True:
            transcribe_response=transcribe.get_transcription_job(TranscriptionJobName=Transcription_Job_Name)
            transcribe_status=transcribe_response['TranscriptionJob']['TranscriptionJobStatus']
            logger.info (f"Transcribe job status: {transcribe_status}")

            if  transcribe_status in ['COMPLETED','FAILED']:
                break
            time.sleep(5)

            if transcribe_status=='COMPLETED':
                TranscriptFileUri=transcribe_response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                logger.info (f"Transcribe job successfully completed. result store in bucket: {target_output_bucket} and file uri: {TranscriptFileUri}")
            
            else:
                logger.error(f"Transcribe job failed: {json.dumps(transcribe_status)}")
                raise Exception["transcribed job has failed"]
    except Exception as e:
        logger.error(f"Error in processing file: {source_key} in lambda function: {lambda_function_name} ")
        return {'statusCode':400,
                'body': json.dumps({'message':'Error in processing file',
                                'error': str(e),
                                'file name':{source_key},
                                'lambda function': {lambda_function_name}})}

    return{'statusCode':200,
           'body': json.dumps({'message':'File processed and transcription result stored successfully',
                                'file name':{source_key},
                                'lambda function': {lambda_function_name}})}
