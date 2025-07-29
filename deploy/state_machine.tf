# Step Function State Machine
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "ecs-bg-test-state-machine"
  role_arn = aws_iam_role.step_function_role.arn

  definition = jsonencode({
    Comment = "A state machine with Lambda execution and manual approval"
    StartAt = "ExecuteLambda"
    States = {
      ExecuteLambda = {
        Type     = "Task"
        Resource = aws_lambda_function.test_lambda.arn
        Next     = "ManualApproval"
      }
      ManualApproval = {
        Type     = "Task"
        Resource = "arn:aws:states:::sns:publish"
        Parameters = {
          TopicArn = aws_sns_topic.approval_topic.arn
          Message  = "Please approve the deployment"
          Subject  = "ECS Blue/Green Deployment Approval Required"
        }
        End = true
      }
    }
  })

  #checkov:skip=CKV_AWS_284: "Ensure State Machine has X-Ray tracing enabled."
  #checkov:skip=CKV_AWS_285: "Ensure State Machine has execution history logging enabled"
  #Reason: Tracing is not required for this StepFunction.
}

# IAM Role for Step Functions
resource "aws_iam_role" "step_function_role" {
  name = "ecs-bg-test-step-function-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Step Functions
resource "aws_iam_role_policy" "step_function_policy" {
  name = "ecs-bg-test-step-function-policy"
  role = aws_iam_role.step_function_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "sns:Publish"
        ]
        Resource = [
          "${aws_lambda_function.test_lambda.arn}",
          "${aws_sns_topic.approval_topic.arn}"
        ]
      }
    ]
  })
}

# Output values
output "state_machine_arn" {
  value = aws_sfn_state_machine.sfn_state_machine.arn
}