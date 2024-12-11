# **Transcription Lambda Function**

This AWS Lambda function processes audio files uploaded to an S3 bucket. It uses Amazon Transcribe to transcribe the audio, redact Personally Identifiable Information (PII), and store the transcription result in a target S3 bucket.

---

## **Features**
- Automatically triggered when an audio file is uploaded to the source S3 bucket.
- Starts an Amazon Transcribe job with PII redaction enabled.
- Stores the transcription result directly in the target S3 bucket.
- Simple workflow with configurable source and target buckets.

---

## **Setup Instructions**

### **1. Permissions Needed**
To ensure the Lambda function works as expected, attach the following permissions to its execution role:

#### **IAM Policies**
- **AmazonS3FullAccess**  
  Or more restrictive permissions:
  - `s3:GetObject`
  - `s3:PutObject`
  - `s3:ListBucket`

- **AmazonTranscribeFullAccess**  
  Or more restrictive permissions:
  - `transcribe:StartTranscriptionJob`
  - `transcribe:GetTranscriptionJob`

- **CloudWatchLogsFullAccess**  
  Or more restrictive permissions:
  - `logs:CreateLogGroup`
  - `logs:CreateLogStream`
  - `logs:PutLogEvents`

---

### **2. Trigger Configuration**
Set up an **S3 Trigger** on the source bucket:

1. **Bucket:** Select the S3 bucket where audio files will be uploaded.  
2. **Event Type:** `s3:ObjectCreated:*` (triggers on file uploads).  
3. **Prefix/Suffix (Optional):** To filter by file type (e.g., `.mp3` or `.wav`).  

---

## **Usage**

1. **Deploy the Lambda Function:**
   - Zip the Lambda function code and upload it to the AWS Lambda console.

2. **Test the Workflow:**
   - Upload an audio file (e.g., `.mp3`, `.wav`) to the source bucket.
   - Monitor logs in **CloudWatch** to confirm the transcription job's progress.

3. **Output:**
   - Transcription results (with PII redaction) will be stored in the target S3 bucket.

---

## **Notes**
- **Supported File Formats:** The audio file must be in a format supported by Amazon Transcribe (e.g., `.mp3`, `.wav`, `.flac`).
- **Language Configuration:** Default language is set to `en-US`. Modify the `LanguageCode` parameter in the code if needed.

---

### **License**
This project is licensed under the [MIT License](LICENSE).  

---

### **Contributions**
Contributions are welcome! Feel free to open issues or submit pull requests to improve the functionality.