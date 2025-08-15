locals {
  # Lambda function ARN - replace this with your actual Lambda ARN reference
  test_lambda_arn        = "arn:aws:lambda:us-east-1:791573251752:function:ecs_deployment_test"
  validation_lambda_arn  = "arn:aws:lambda:us-east-1:791573251752:function:ecs_deployment_validation"
  POST_SCALE_UP          = "arn:aws:lambda:us-east-1:791573251752:function:ecs_POST_SCALE_UP"
  lambda_iam_role_arn    = "arn:aws:iam::791573251752:role/dd-ecsLoadBalancer-Role"
  test_lambda_name       = "ecs_deployment_test"
  validation_lambda_name = "ecs_deployment_validation"
  cluster_name           = "ecs-bg-deployment-test"
  service_name           = "ecs-bg-deployment-test-service"

  # appspec file
  appspec = {
    version = "0.0"
    Resources = [
      {
        TargetService = {
          Type = "AWS::ECS::Service"
          Properties = {
            TaskDefinition = aws_ecs_task_definition.web_app.arn
            LoadBalancerInfo = {
              ContainerName = "first"
              ContainerPort = 8080
            }
          }
        }
      }
    ]
    Hooks = [
      {
        AfterInstall = local.test_lambda_name
      },
      {
        BeforeAllowTraffic = local.validation_lambda_name
      }
    ]
  }

  appspec_content = replace(jsonencode(local.appspec), "\"", "\\\"")
  appspec_sha256  = sha256(jsonencode(local.appspec))

  # create deployment script
  script = <<EOF
#!/bin/bash
set -e

echo "Starting CodeDeploy agent deployment"
aws --version

echo "Constructing deployment command..."
COMMAND=$(cat <<EOT
aws deploy create-deployment \
    --application-name "${aws_codedeploy_app.application_main.name}" \
    --deployment-config-name CodeDeployDefault.ECSAllAtOnce \
    --deployment-group-name "${aws_codedeploy_deployment_group.application_main.deployment_group_name}" \
    --revision '{"revisionType": "AppSpecContent", "appSpecContent": {"content": "${local.appspec_content}", "sha256":"${local.appspec_sha256}"}}' \
    --description "Deployment from Terraform" \
    --output json

aws ecs update-service \
    --cluster "${local.cluster_name}" \
    --service "${local.service_name}" \
    --task-definition "${aws_ecs_task_definition.web_app.arn}" \
    --deployment-configuration '{"deploymentCircuitBreaker":{"enable":true,"rollback":true},"maximumPercent":200,"minimumHealthyPercent":100,"strategy":"BLUE_GREEN","lifecycleHooks":[{"lifecycleStages":["POST_SCALE_UP"], "roleArn": "${local.lambda_iam_role_arn}","hookTargetArn":"${aws_lambda_function.test_lambda.arn}"}]}' \
    --service-connect-configuration '{"enabled":false}'

EOT
)

echo "AWS CLI VERSION"
echo "$(aws --version)"

echo "Command to be executed:"
echo "$COMMAND"

echo "Executing deployment command..."
DEPLOYMENT_INFO=$(eval "$COMMAND")
COMMAND_EXIT_CODE=$?

echo "Command exit code: $COMMAND_EXIT_CODE"
echo "Raw output:"
echo "$DEPLOYMENT_INFO"

if [ $COMMAND_EXIT_CODE -ne 0 ]; then
    echo "Error: AWS CLI command failed"
    exit $COMMAND_EXIT_CODE
fi

echo "Parsing deployment info..."
if ! DEPLOYMENT_ID=$(echo "$DEPLOYMENT_INFO" | jq -r '.deploymentId'); then
    echo "Error: Failed to parse deployment ID from output"
    exit 1
fi

if [ "$DEPLOYMENT_ID" == "null" ] || [ -z "$DEPLOYMENT_ID" ]; then
    echo "Error: Deployment ID is null or empty"
    exit 1
fi

echo "Deployment ID: $DEPLOYMENT_ID"

echo "Deployment created successfully"
EOF
}



#Create the code_deploy.sh file to run the AWS CodeDeploy deployment
#https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
resource "local_file" "code_deploy_sh" {
  content         = local.script
  filename        = "${path.module}/code_deploy.sh"
  file_permission = "0755"
  depends_on = [
    aws_codedeploy_app.application_main,
    aws_codedeploy_deployment_group.application_main,
    aws_ecs_task_definition.web_app
  ]
}

#https://developer.hashicorp.com/terraform/language/resources/terraform-data
resource "terraform_data" "trigger_code_deploy_deployment" {
  triggers_replace = local_file.code_deploy_sh
  provisioner "local-exec" {
    command     = "./code_deploy.sh"
    interpreter = ["/bin/bash", "-c"]
  }
  depends_on = [local_file.code_deploy_sh]
  lifecycle {
    replace_triggered_by = [local_file.code_deploy_sh]
  }
}