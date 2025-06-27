# SNS Topic
resource "aws_sns_topic" "approval_topic" {
  name = "ecs-bg-test-sns"
}

# SNS Topic Subscription
resource "aws_sns_topic_subscription" "approval_target" {
  topic_arn = aws_sns_topic.approval_topic.arn
  protocol  = "email"
  endpoint  = "desadipe@amazon.com"
}

# Output values
output "sns_topic_arn" {
  value = aws_sns_topic.approval_topic.arn
}