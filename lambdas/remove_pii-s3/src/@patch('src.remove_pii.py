   @patch('src.remove_pii.transcribe_client')
    @patch('time.sleep', return_value=None)
    def test_lambda_handler_in_progress(self,mock_sleep,moc_transcribe_client):
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "test-file.mp3"}
                }
            }]
        }
        context={}
        moc_transcribe_client.start_transcription_job.return_value={"TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}}
        moc_transcribe_client.check_transcription_status.return_value='COMPLETED'
        response=handler.lambda_handler(event, context)
        self.assertEqual(response["Status"], "COMPLETED")