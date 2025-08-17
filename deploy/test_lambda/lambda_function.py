import boto3
import json
import logging
import os
import random
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
codedeploy = boto3.client('codedeploy')
ssm = boto3.client('ssm')
sfn_client = boto3.client('stepfunctions')

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
        execution_id = f"execution-{event['executionId']}"

        return_response = {"hookStatus": "IN_PROGRESS", "callBackDelay": 30}

        # Start state machine execution
        try:
            response = sfn_client.describe_execution(
                executionArn=f"arn:aws:states:us-east-1:791573251752:execution:ecs-bg-test-state-machine:{execution_id}"
            )
            
            # Extract relevant information
            status = response['status']

            logger.info(f"Execution ID FOUND: {execution_id}")

            response = ssm.get_parameter(
                    Name='POST_SCALE_UP',
                    WithDecryption=False
                )

            if status == "SUCCEEDED":
                if response["Parameter"]["Value"] == "SUCCEEDED":
                    return_response = {"hookStatus": "SUCCEEDED"}
                elif response["Parameter"]["Value"] == "FAILED":
                    return_response = {"hookStatus": "FAILED"}
                else:
                    return_response = {"hookStatus": "IN_PROGRESS", "callBackDelay": 30}
                    logger.info(f"Step Fn Status: {status} - SSM PARA Value: {response["Parameter"]["Value"]}")
    

        except sfn_client.exceptions.ExecutionDoesNotExist:
            logger.info(f"Execution ID not found: {execution_id} - Starting a new Execution")

            response = sfn_client.start_execution(
                stateMachineArn=os.environ.get('STATE_MACHINE_ARN'),
                name=f"execution-{event['executionId']}",
                input=json.dumps(event)
            )

            # Write to SSM Parameter Store
            response = ssm.put_parameter(
                Name='POST_SCALE_UP',
                Value="IN_PROGRESS",
                Type='String',
                Overwrite=True
            )
            logger.info(f"State machine execution started: {response}")

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
