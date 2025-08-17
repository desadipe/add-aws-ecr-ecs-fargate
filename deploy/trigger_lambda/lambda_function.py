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
ssm = boto3.client("ssm")


def lambda_handler(event, context):
    try:
        logger.info(f"Lambda: ecs_STPFN_TEST_tf Received event: {json.dumps(event)}")
        a = random.randint(1, 100)

        ##################################################
        # VALIDATION TESTS  --- VALID RESPONSE >> SUCCEEDED, FAILED, IN_PROGRESS
        ##################################################
        for i in range(5):
            x = random.randint(0, 5)
            time.sleep(a)
            logger.info(
                f"Loop iteration: {i} --- Random number: {x} --- Sleep {a} seconds"
            )

            if i == 4 or x == 0:
                hookStatus = "SUCCEEDED"
                break
            elif x == 6:
                hookStatus = "FAILED"

        response = ssm.put_parameter(
            Name="POST_SCALE_UP", Value=hookStatus, Type="String", Overwrite=True
        )

        logger.info(
            f"SSM POST_SCALE_UP Parameter Write Response: {json.dumps(response)}"
        )
        return response

    except ClientError as e:
        print(f"Error starting state machine: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": str(e), "message": "Failed to start state machine execution"}
            ),
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "message": "Internal server error"}),
        }
