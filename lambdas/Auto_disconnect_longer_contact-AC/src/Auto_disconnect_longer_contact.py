import json
import os
from datetime import datetime, timezone
import boto3
import botocore.exceptions
from common.logger import Logger

# Initialize the custom logger
LOGGER = Logger(__name__)

# Environment variables with proper type conversion
ACTIVE_TIME = float(os.getenv('ACTIVE_TIME', '5'))  # Convert to float, time in hours
UPDATE_TIME = float(os.getenv('UPDATE_TIME', '2'))  # Convert to float, time in hours
INSTANCE = os.getenv('INSTANCE', 'arn:aws:connect:us-east-1:123456789012:instance/abcd1234-efgh-5678-ijkl-9012mnop3456')
REGION = os.getenv('REGION', 'us-east-1')

connect_client = boto3.client('connect', region_name=REGION)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        return super().default(obj)


def fetch_routing_profiles_arn():
    """
    Fetch all routing profile ARNs from the Amazon Connect instance.

    Returns:
        list: A list of routing profile ARNs
    """
    try:
        LOGGER.info(f"Fetching routing profiles for instance {INSTANCE}")
        paginator = connect_client.get_paginator('list_routing_profiles')
        response_iterator = paginator.paginate(InstanceId=INSTANCE)

        routing_profile_arns = []
        for page in response_iterator:
            for profile in page.get('RoutingProfileSummaryList', []):
                routing_profile_arns.append(profile['Arn'])

        LOGGER.info(f"Found {len(routing_profile_arns)} routing profiles")
        return routing_profile_arns
    except Exception as e:
        LOGGER.error(f"Error fetching routing profiles: {str(e)}")
        raise e


def fetch_contacts(routing_profile_batch):
    """
    Fetch contacts that have been connected to agents for longer than ACTIVE_TIME.

    Args:
        routing_profile_batch (list): A batch of routing profile ARNs

    Returns:
        list: A list of contact IDs that meet the criteria
    """
    try:
        LOGGER.info(f"Fetching contacts for {len(routing_profile_batch)} routing profiles")
        response = connect_client.get_current_user_data(
            InstanceId=INSTANCE,
            Filter={
                'RoutingProfiles': routing_profile_batch,
                'ContactFilter': {
                    'ContactStates': ['CONNECTED']
                }
            }
        )

        active_contact = []
        now = datetime.now(timezone.utc)

        for user in response['UserDataList']:
            for contact in user['Contacts']:
                connected_to_agent_timestamp = contact.get('ConnectedToAgentTimestamp')

                if not connected_to_agent_timestamp:
                    continue

                if isinstance(connected_to_agent_timestamp, str):
                    connected_to_agent_timestamp = datetime.fromisoformat(connected_to_agent_timestamp)

                if isinstance(connected_to_agent_timestamp, datetime):
                    # Calculate hours since connection
                    connected_hours = (now - connected_to_agent_timestamp).total_seconds() / 3600

                    if connected_hours >= ACTIVE_TIME:
                        LOGGER.info(
                            f"Contact {contact['ContactId']} connected for {connected_hours:.2f} hours, exceeds threshold of {ACTIVE_TIME} hours")
                        active_contact.append(contact['ContactId'])

        LOGGER.info(f"Found {len(active_contact)} contacts exceeding active time threshold")
        return active_contact

    except Exception as e:
        LOGGER.error(f"Error fetching contacts: {str(e)}")
        raise e


def describe_contact(contact_id):
    """
    Get detailed information about a specific contact.

    Args:
        contact_id (str): The ID of the contact to describe

    Returns:
        dict: Contact information including timestamps and status
    """
    try:
        LOGGER.info(f"Describing contact {contact_id}")
        response = connect_client.describe_contact(
            InstanceId=INSTANCE,
            ContactId=contact_id
        )

        # Determine if contact is complete based on whether DisconnectTimestamp exists
        contact_status = 'Complete' if response['Contact'].get('DisconnectTimestamp') else 'In-progress'

        return {
            "status": 200,
            "message": "Success",
            "data": {
                "LastUpdateTimestamp": response['Contact']['LastUpdateTimestamp'],
                "ConnectedToAgentTimestamp": response['Contact']['AgentInfo']['ConnectedToAgentTimestamp'],
                "status": contact_status,
            }
        }
    except Exception as e:
        LOGGER.error(f"Error describing contact {contact_id}: {str(e)}")
        raise e


def should_disconnect(contact_details):
    """
    Determine if a contact should be disconnected based on its last update time.
    Returns True if the contact should be disconnected.

    Args:
        contact_details (dict): Contact details from describe_contact

    Returns:
        bool: True if the contact should be disconnected, False otherwise
    """
    try:
        last_update = contact_details['data']['LastUpdateTimestamp']

        if not last_update:
            LOGGER.warning("Missing 'LastUpdateTimestamp' in contact data")
            return False

        if isinstance(last_update, str):
            last_update = datetime.fromisoformat(last_update)

        if isinstance(last_update, datetime):
            now = datetime.now(timezone.utc)
            # Calculate hours since last update
            hours_since_update = (now - last_update).total_seconds() / 3600

            # If no activity for longer than UPDATE_TIME hours, disconnect
            should_disconnect = hours_since_update >= UPDATE_TIME

            LOGGER.info(
                f"Contact last updated {hours_since_update:.2f} hours ago. Should disconnect: {should_disconnect}")
            return should_disconnect

        return False

    except Exception as e:
        LOGGER.error(f"Error determining if contact should be disconnected: {str(e)}")
        raise e


def disconnect_contact(contact_id):
    """
    Disconnect a contact and verify the action.

    Args:
        contact_id (str): The ID of the contact to disconnect

    Returns:
        dict: Result of the disconnect operation
    """
    try:
        LOGGER.info(f"Attempting to disconnect contact {contact_id}")

        connect_client.stop_contact(
            ContactId=contact_id,
            InstanceId=INSTANCE,
            DisconnectReason={
                'DISCONNECT_CAUSE': 'LONGER_RUNNING_CONTACT'
            }
        )

        # Give a short delay to allow the disconnect to process
        import time
        time.sleep(2)

        # Check if disconnect was successful
        check_status = describe_contact(contact_id)
        contact_status = check_status['data']['status']

        if contact_status == 'Complete':
            result_status = 'Successful'
        elif contact_status == 'In-progress':
            result_status = 'Failed'
        else:
            result_status = 'Not_Found'

        LOGGER.info(f"Disconnect result for contact {contact_id}: {result_status}")

        return {
            "status": 200,
            "message": "Success",
            "data": {
                'contact_id': contact_id,
                "contact_status": result_status,
            }
        }
    except Exception as e:
        LOGGER.error(f"Error disconnecting contact {contact_id}: {str(e)}")
        raise e


def lambda_handler(event, context):
    """
    Main Lambda handler function.

    Args:
        event (dict): Lambda event
        context (LambdaContext): Lambda context

    Returns:
        dict: Result of the operation
    """
    LOGGER.info("Starting contact management Lambda function")

    try:
        active_contacts = []
        arn_limit = 100  # Max limit for batch operations

        # Fetch all routing profiles
        routing_profile_arns = fetch_routing_profiles_arn()

        # Process routing profiles in batches
        for i in range(0, len(routing_profile_arns), arn_limit):
            arn_batch = routing_profile_arns[i:i + arn_limit]
            active_contacts.extend(fetch_contacts(arn_batch))

        LOGGER.info(f"Processing {len(active_contacts)} active contacts")

        # Process each active contact
        contact_results = []
        for contact_id in active_contacts:
            try:
                # Get contact details
                contact_details = describe_contact(contact_id)

                # Determine if contact should be disconnected
                disconnect_required = should_disconnect(contact_details)

                if disconnect_required:
                    # Disconnect the contact
                    disconnect_result = disconnect_contact(contact_id)
                    contact_status = disconnect_result['data']['contact_status']
                else:
                    contact_status = 'Skip Disconnection'

                # Record the result
                contact_results.append({
                    'Status': contact_status,
                    'Contact_id': contact_id,
                    "LastUpdateTimestamp": contact_details['data']['LastUpdateTimestamp'],
                    "ConnectedToAgentTimestamp": contact_details['data']['ConnectedToAgentTimestamp']
                })

            except Exception as e:
                LOGGER.error(f"Error processing contact {contact_id}: {str(e)}")
                contact_results.append({
                    'Status': 'Error',
                    'Contact_id': contact_id,
                    'Error': str(e)
                })

        # Return the results
        return {
            "status": 200,
            "message": "Success",
            "data": {
                'contact_result': json.loads(json.dumps(contact_results, cls=DateTimeEncoder)),
                'contacts_processed': len(active_contacts),
                'contacts_disconnected': sum(1 for result in contact_results if result['Status'] == 'Successful')
            }
        }

    except botocore.exceptions.NoCredentialsError:
        LOGGER.error("No AWS credentials found")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "No AWS credentials found"})
        }

    except botocore.exceptions.PartialCredentialsError:
        LOGGER.error("Incomplete AWS credentials")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Incomplete AWS credentials"})
        }

    except botocore.exceptions.ClientError as e:
        LOGGER.error(f"AWS Client Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "AWS Client Error", "message": str(e)})
        }

    except Exception as e:
        LOGGER.error(f"Unhandled exception: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error", "message": str(e)})
        }