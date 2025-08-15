import boto3
import json
import logging
import random
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize CodeDeploy client
codedeploy = boto3.client('codedeploy')
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    """
    AWS Lambda function to handle CodeDeploy lifecycle events
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
    Returns:
        dict: Response object containing status and message
    """
    try:
        ##################################################
        # GET INPUT VARIABLES
        ##################################################
        # Log the received event
        logger.info(f"Received event: {json.dumps(event)}")

        ##################################################
        # VALIDATION TESTS
        ##################################################
        # SUCCEEDED, FAILED, IN_PROGRESS
        x = random.randint(0, 5)
        logger.info(f"Random number: {x}")
        
        if (x == 0):
            hookStatus = 'SUCCEEDED'
            return_response = {"hookStatus": "SUCCEEDED"}
        elif (x == 6):
            hookStatus = 'FAILED'
            return_response = {"hookStatus": "FAILED"}
        else:
            hookStatus = 'IN_PROGRESS'
            return_response = {"hookStatus": "IN_PROGRESS", "callBackDelay": 30}

        # Write to SSM Parameter Store
        response = ssm.put_parameter(
            Name='POST_SCALE_UP',
            Value=hookStatus,
            Type='String',
            Overwrite=True
        )

        ##################################################
        # GENERATE RESPONSE
        ##################################################
        logger.info("Return Response: {}".format(json.dumps(return_response)))
        return return_response

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Validation error: {str(ve)}",
                'status': 'Failed'
            })
        }

    except ClientError as ce:
        logger.error(f"AWS API error: {str(ce)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"AWS API error: {str(ce)}",
                'status': 'Failed'
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Unexpected error: {str(e)}",
                'status': 'Failed'
            })
        }
