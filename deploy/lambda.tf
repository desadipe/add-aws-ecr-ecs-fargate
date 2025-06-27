# Create zip file from lambda code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"  # Directory containing your lambda code
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda Function
resource "aws_lambda_function" "test_lambda" {
  filename      = "lambda_function.zip"
  function_name = "ecs-bg-lambda-test-tf"
  role          = "arn:aws:iam::791573251752:role/dd-lambdaSSMFullAccess-Role"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
}

# Output values
output "test_lambda_arn" {
  value = aws_lambda_function.test_lambda.arn
}