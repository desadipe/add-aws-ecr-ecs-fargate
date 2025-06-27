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

        # Read the DeploymentId from the event payload
        deployment_id = event.get('DeploymentId')
        if not deployment_id:
            raise ValueError("DeploymentId not found in event payload")

        # Read the LifecycleEventHookExecutionId from the event payload
        lifecycle_event_hook_execution_id = event.get('LifecycleEventHookExecutionId')
        if not lifecycle_event_hook_execution_id:
            raise ValueError("LifecycleEventHookExecutionId not found in event payload")

        logger.info(f"Processing deployment_id: {deployment_id}")
        logger.info(f"Lifecycle event hook execution_id: {lifecycle_event_hook_execution_id}")

        ##################################################
        # VALIDATION TESTS
        ##################################################
        if (random.randint(0, 1) == 0):
            status = 'Succeeded'
        else:
            status = 'Failed'
        
        # Validate the status value
        if status not in ['Succeeded', 'Failed']:
            raise ValueError("Invalid status value. Must be 'Succeeded' or 'Failed'")

        # Write to SSM Parameter Store
        response = ssm.put_parameter(
            Name='automated_test_status',
            Value=status,
            Type='String',
            Overwrite=True
        )

        ##################################################
        # GENERATE RESPONSE
        ##################################################
        # Prepare the validation test results
        params = {
            'deploymentId': deployment_id,
            'lifecycleEventHookExecutionId': lifecycle_event_hook_execution_id,
            'status': status  # 'Succeeded' or 'Failed'
        }

        # Pass CodeDeploy the prepared validation test results
        logger.info(f"Updating lifecycle event status with params: {params}")
        response = codedeploy.put_lifecycle_event_hook_execution_status(**params)

        message = 'Validation test succeeded' if status == 'Succeeded' else 'Validation test failed'
        logger.info(message)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': message,
                'status': status,
                'deploymentId': deployment_id,
                'response': response
            })
        }

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
