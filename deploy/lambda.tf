################################################################################
# Create zip file from lambda code
data "archive_file" "test_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/test_lambda" # Directory containing your lambda code
  output_path = "${path.module}/test_lambda.zip"
}

# Lambda Function
resource "aws_lambda_function" "test_lambda" {
  filename      = "test_lambda.zip"
  function_name = "ecs-bg-lambda-test-tf"
  role          = "arn:aws:iam::791573251752:role/dd-lambdaSSMFullAccess-Role"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
}

# Output values
output "test_lambda_arn" {
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
  filename      = "trigger_lambda.zip"
  function_name = "ecs-bg-lambda-trigger-tf"
  role          = "arn:aws:iam::791573251752:role/dd-lambdaSSMFullAccess-Role"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"

  # Add environment variables
  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.sfn_state_machine.arn
    }
  }
}

# Output values
output "trigger_lambda_arn" {
  value = aws_lambda_function.trigger_lambda.arn
}