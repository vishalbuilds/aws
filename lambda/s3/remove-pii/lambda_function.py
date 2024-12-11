
# Lambda function to redact pii information.

import boto3
import uuid
import time
import json

def generate_random_id():
    return str(uuid.uuid4())


transcribe = boto3.client('transcribe')

def lambda_handler(event,context):
    source_bucket= event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    target_output_bucket="new-recording-with-pii"

    job_id= generate_random_id()

    Transcription_Job_Name=f"Transcription_Job_Name-{job_id}"
    Media_File_Uri=f"s3://{source_bucket}/{source_key}"

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=Transcription_Job_Name,
            LanguageCode='en-US'
            Media={'MediaFileUri': Media_File_Uri},
            ContentRedaction={'RedactionType': 'PII',
                              'RedactionOutput': 'redacted'},
            OutputBucketName=target_output_bucket,
        )
        print("started transcribe job"+Transcription_Job_Name)
        
        while True:
            transcribe_response=transcribe.get_transcription_job(
                TranscriptionJobName=Transcription_Job_Name)
            if transcribe_response['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED','FAILED']:
                break
            time.sleep(5)
        if transcribe_response['TranscriptionJob']['TranscriptionJobStatus']=='COMPLETED':
            TranscriptFileUri=transcribe_response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            print('succefully transcribed the PII')
        else:
            raise Exception["transcribed job has been failed"]
    except Exception as e:
        print(f"error processing file {source_key}: {e}")

    return{
        'statusCode':200,
        'body': json.dumps('file processed and transcription result stored successfully')
    }
        



        

            
            








