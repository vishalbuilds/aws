
from remove_pii import lambda_handler
contxt={
    'function_name':'remove-pii',
    'function_version':'1',
    'invoked_function_arn':'arn:aws:lambda:us-east-1:123456789012:function:remove-pii',
    'memory_limit_in_mb':'128',
    'log_group_name':'/aws/lambda/remove-pii',
    'log_stream_name':'2021/09/13/[$LATEST]12345678901234567890123456789012',
    'client_context':'',
    'identity':''
}
event={
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2025-02-24T12:34:56.789Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AWS:EXAMPLEUSER"
      },
      "requestParameters": {
        "sourceIPAddress": "192.168.1.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLEabcdefghijklmnopqrstuv"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "exampleConfigRule",
        "bucket": {
          "name": "my-example-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLEOWNER"
          },
          "arn": "arn:aws:s3:::my-example-bucket"
        },
        "object": {
          "key": "uploads/my-file.txt",
          "size": 1024,
          "eTag": "123456789abcdef123456789abcdef12",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}




lambda_handler(event,contxt)
