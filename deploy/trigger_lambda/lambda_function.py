# lambda/index.py

import json
import boto3
import os
import random
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SSM client
ssm = boto3.client('ssm')

STATE_MACHINE_INFO = os.environ.get('STATE_MACHINE_INFO')

def handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # TEST 1
        a = random.randint(1, 100)
        b = random.randint(99, 199)
        logger.info(f"Random numbers: {a} + {b}")

        # Write to SSM Parameter Store
        response = ssm.put_parameter(
            Name=STATE_MACHINE_INFO,
            Value=f'{a} + {b} = {a+b}',
            Type='String',
            Overwrite=True
        )
        logger.info(f"SSM Write Response: {json.dumps(response)}")

        return response

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
