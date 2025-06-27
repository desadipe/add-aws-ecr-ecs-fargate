# lambda/index.py

import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize AWS clients
sfn_client = boto3.client('stepfunctions')

# Get state machine ARN from environment variable
STATE_MACHINE_ARN = os.environ.get('STATE_MACHINE_ARN')

def handler(event, context):
    try:
        # Generate a unique execution name using timestamp
        execution_name = f"execution-{context.aws_request_id}"

        # Prepare input for state machine
        state_machine_input = {
            "deploymentId": event.get('deploymentId', ''),
            "hookId": event.get('hookId', ''),
            "timestamp": event.get('timestamp', ''),
            "originalEvent": event
        }

        # Start state machine execution
        response = sfn_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=execution_name,
            input=json.dumps(state_machine_input)
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'State machine execution started successfully',
                'executionArn': response['executionArn'],
                'startDate': str(response['startDate'])
            })
        }

    except ClientError as e:
        print(f"Error starting state machine: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to start state machine execution'
            })
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            })
        }
