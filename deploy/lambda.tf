# Lambda Function (assuming it exists - include its definition if needed)
resource "aws_lambda_function" "test_lambda" {
  filename      = "lambda_function.zip"
  function_name = "ecs-bg-lambda-test-tf"
  role          = "arn:aws:iam::791573251752:role/dd-lambdaSSMFullAccess-Role"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"

  # Add other Lambda configuration as needed
}

# Output values
output "test_lambda_arn" {
  value = aws_lambda_function.test_lambda.arn
}