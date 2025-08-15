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

        # Start state machine execution
        try:
            response = sfn_client.describe_execution(
                executionArn=f"arn:aws:states:us-east-1:791573251752:execution:ecs-bg-test-state-machine:{execution_id}"
            )
            
            # Extract relevant information
            status = response['status']
            start_date = response['startDate'].strftime('%Y-%m-%d %H:%M:%S')

            logger.info(f"Execution ID FOUND: {execution_id} - Status: {status} - Start Date: {start_date}")

            # # Get end date if execution is completed
            # end_date = None
            # if 'stopDate' in response:
            #     end_date = response['stopDate'].strftime('%Y-%m-%d %H:%M:%S')

            # # Store status in SSM
            # ssm.put_parameter(
            #     Name='/POST_SCALE_UP/state-machine-execution-status',
            #     Value=status,
            #     Type='String',
            #     Overwrite=True
            # )

            # # Store datetime in SSM if execution is completed
            # if end_date:
            #     ssm.put_parameter(
            #         Name='/POST_SCALE_UP/state-machine-execution-date-time',
            #         Value=end_date,
            #         Type='String',
            #         Overwrite=True
            #     )

            # execution_info = {
            #     'executionId': execution_id,
            #     'status': status,
            #     'startDate': start_date,
            #     'endDate': end_date,
            #     'input': json.loads(response['input']) if 'input' in response else None,
            #     'output': json.loads(response['output']) if 'output' in response else None
            # }

            # logger.info(f"Execution info: {json.dumps(execution_info, indent=2)}")

            # return {
            #     'statusCode': 200,
            #     'body': json.dumps(execution_info)
            # }

        except sfn_client.exceptions.ExecutionDoesNotExist:
            message = f"Execution ID not found: {execution_id} - Starting a new Execution"
            response = sfn_client.start_execution(
                stateMachineArn=os.environ.get('STATE_MACHINE_ARN'),
                name=f"execution-{event['executionId']}",
                input=json.dumps(event)
            )
            logger.info(f"State machine execution started: {response}")

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
