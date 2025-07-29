# SNS Topic
resource "aws_sns_topic" "approval_topic" {
  name = "ecs-bg-test-sns"
}

# SNS Topic Subscription
resource "aws_sns_topic_subscription" "approval_target" {
  topic_arn = aws_sns_topic.approval_topic.arn
  protocol  = "email"
  endpoint  = "desadipe@amazon.com"

  #checkov:skip=CKV_AWS_26: "Ensure all data stored in the SNS topic is encrypted"
  #Reason: Encryption is NOT required for this topic.
}

# Output values
output "sns_topic_arn" {
  value = aws_sns_topic.approval_topic.arn
}