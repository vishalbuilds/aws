import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timezone,timedelta
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import Auto-disconnect-longer-contact as handler

class TestLambdaFunction(unittest.TestCase):

    @patch('your_lambda_script.connect_client')
    def test_fetch_routing_profiles_arn(self, mock_connect_client):
        """Test fetching routing profiles."""
        mock_connect_client.get_paginator.return_value.paginate.return_value = [
            {'RoutingProfileSummaryList': [{'Arn': 'arn1'}, {'Arn': 'arn2'}]}
        ]

        result = handler.fetch_routing_profiles_arn()
        self.assertEqual(result, ['arn1', 'arn2'])

    @patch('your_lambda_script.connect_client')
    def test_fetch_contacts(self, mock_connect_client):
        """Test fetching active contacts."""
        mock_connect_client.get_current_user_data.return_value = {
            'UserDataList': [{
                'Contacts': [{
                    'ContactId': 'contact1',
                    'ConnectedToAgentTimestamp': (datetime.now(timezone.utc).isoformat())
                }]
            }]
        }

        result = handler.fetch_contacts(['arn1'])
        self.assertIn('contact1', result)

    @patch('your_lambda_script.connect_client')
    def test_describe_contact(self, mock_connect_client):
        """Test describing a contact."""
        mock_connect_client.describe_contact.return_value = {
            'Contact': {
                'LastUpdateTimestamp': datetime.now(timezone.utc).isoformat(),
                'AgentInfo': {'ConnectedToAgentTimestamp': datetime.now(timezone.utc).isoformat()}
            }
        }

        result = handler.describe_contact('contact1')
        self.assertEqual(result['status'], 200)
        self.assertIn('LastUpdateTimestamp', result['data'])

    def test_should_disconnect(self):
        """Test should_disconnect logic."""
        last_update_time = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        contact_details = {
            "data": {
                "LastUpdateTimestamp": last_update_time
            }
        }

        os.environ['UPDATE_TIME'] = '2'
        result = handler.handler.should_disconnect(contact_details)
        self.assertTrue(result)

    @patch('your_lambda_script.connect_client')
    def test_disconnect_contact(self, mock_connect_client):
        """Test disconnecting a contact."""
        mock_connect_client.stop_contact.return_value = {}

        with patch('your_lambda_script.describe_contact', return_value={'data': {'status': 'Complete'}}):
            result = handler.disconnect_contact('contact1')
            self.assertEqual(result['data']['contact_status'], 'Successful')

    @patch('your_lambda_script.fetch_routing_profiles_arn', return_value=['arn1'])
    @patch('your_lambda_script.fetch_contacts', return_value=['contact1'])
    @patch('your_lambda_script.describe_contact', return_value={'data': {'LastUpdateTimestamp': datetime.now(timezone.utc).isoformat()}})
    @patch('your_lambda_script.should_disconnect', return_value=True)
    @patch('your_lambda_script.disconnect_contact', return_value={'data': {'contact_status': 'Successful'}})
    def test_lambda_handler(self, mock_fetch_routing, mock_fetch_contacts, mock_describe, mock_should_disconnect, mock_disconnect):
        """Test the main lambda handler."""
        event = {}
        context = {}

        result = handler.lambda_handler(event, context)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['data']['contacts_disconnected'], 1)


if __name__ == '__main__':
    unittest.main()
