terraform {
  backend "s3" {
    bucket  = "ecs-bg-deploy-gallup-20250602"
    encrypt = true
    key     = "tf/add-aws-ecr-ecs-fargate/deploy-ecs.tfstate"
    region  = "us-east-1"
  }
}