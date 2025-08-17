################################################################################
# Create zip file from lambda code
data "archive_file" "test_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/test_lambda" # Directory containing your lambda code
  output_path = "${path.module}/test_lambda.zip"
}

# Lambda Function
resource "aws_lambda_function" "test_lambda" {
  filename         = "${path.module}/test_lambda.zip"
  source_code_hash = data.archive_file.test_lambda_zip.output_base64sha256
  function_name    = "ecs_POST_SCALE_UP_tf"
  role             = "arn:aws:iam::791573251752:role/dd-lambdaSSMFullAccess-Role"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"

  # Add environment variables
  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.sfn_state_machine.arn
    }
  }

  #checkov:skip=CKV_AWS_50: "X-Ray tracing is enabled for Lambda"
  #checkov:skip=CKV_AWS_115: "Ensure that AWS Lambda function is configured for function-level concurrent execution limit"
  #checkov:skip=CKV_AWS_116: "Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)"
  #checkov:skip=CKV_AWS_117: "Ensure that AWS Lambda function is configured inside a VPC"
  #checkov:skip=CKV_AWS_173: "Check encryption settings for Lambda environmental variable"
  #checkov:skip=CKV_AWS_272: "Ensure AWS Lambda function is configured to validate code-signing"
}

# Output values
output "ecs_POST_SCALE_UP_tf_arn" {
  value = aws_lambda_function.test_lambda.arn
}

################################################################################
# Create zip file from lambda code
data "archive_file" "trigger_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/trigger_lambda" # Directory containing your lambda code
  output_path = "${path.module}/trigger_lambda.zip"
}

# Lambda Function
resource "aws_lambda_function" "trigger_lambda" {
  filename         = "${path.module}/trigger_lambda.zip"
  source_code_hash = data.archive_file.trigger_lambda_zip.output_base64sha256
  function_name    = "ecs_STPFN_TEST_tf"
  role             = "arn:aws:iam::791573251752:role/dd-lambdaSSMFullAccess-Role"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  timeout          = 600

  #checkov:skip=CKV_AWS_50: "X-Ray tracing is enabled for Lambda"
  #checkov:skip=CKV_AWS_115: "Ensure that AWS Lambda function is configured for function-level concurrent execution limit"
  #checkov:skip=CKV_AWS_116: "Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)"
  #checkov:skip=CKV_AWS_117: "Ensure that AWS Lambda function is configured inside a VPC"
  #checkov:skip=CKV_AWS_173: "Check encryption settings for Lambda environmental variable"
  #checkov:skip=CKV_AWS_173: "Check encryption settings for Lambda environmental variable"
  #checkov:skip=CKV_AWS_272: "Ensure AWS Lambda function is configured to validate code-signing"
}

# Output values
output "trigger_lambda_arn" {
  value = aws_lambda_function.trigger_lambda.arn
}