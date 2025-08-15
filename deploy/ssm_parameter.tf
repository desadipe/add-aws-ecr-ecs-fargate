#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter
resource "aws_ssm_parameter" "state_machine_info" {
  # name        = "/${aws_sfn_state_machine.sfn_state_machine.name}/info"
  name        = "/ecs-bg-test-state-machine/info"
  description = "State Machine Execution Information"
  type        = "String"
  value       = "initial_value"
  lifecycle {
    ignore_changes = [value]
  }

  #checkov:skip=CKV2_AWS_34: "AWS SSM Parameter should be Encrypted"
}
