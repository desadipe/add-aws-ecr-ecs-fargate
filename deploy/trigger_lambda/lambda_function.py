import boto3
import json
import logging
import os
import random
import time
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SSM client
ssm = boto3.client('ssm')

STATE_MACHINE_INFO = os.environ.get('STATE_MACHINE_INFO')

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        ##################################################
        # VALIDATION TESTS 1
        ##################################################
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
        logger.info(f"SSM STATE_MACHINE_INFO Write Response: {json.dumps(response)}")
        
        ##################################################
        # VALIDATION TESTS 2
        ##################################################
        # SUCCEEDED, FAILED, IN_PROGRESS
        for i in range(5):
            x = random.randint(0, 5)
            time.sleep(a)
            logger.info(f"Loop iteration: {i} --- Random number: {x} --- Sleep {a} seconds")

            if (i == 4 or x == 0):
                hookStatus = 'SUCCEEDED'
                break
            elif (x == 6):
                hookStatus = 'FAILED'

        response = ssm.put_parameter(
            Name='POST_SCALE_UP',
            Value=hookStatus,
            Type='String',
            Overwrite=True
        )

        logger.info(f"SSM POST_SCALE_UP Write Response: {json.dumps(response)}")
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
