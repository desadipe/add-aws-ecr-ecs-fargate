# Lambda Function (assuming it exists - include its definition if needed)
resource "aws_lambda_function" "test_lambda" {
  filename      = "lambda_function.zip"
  function_name = "ecs-bg-lambda-test-tf"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13"

  # Add other Lambda configuration as needed
}

# Output values
output "state_machine_arn" {
  value = aws_lambda_function.test_lambda.arn
}