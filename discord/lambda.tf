resource "aws_lambda_function" "blut_aws_tf_minecraft_lambda" {
  function_name = "blut_aws_tf_minecraft_lambda"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_load_python_artifact.key

  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"

  source_code_hash = filebase64sha256("${path.module}/deployment_package.zip")

  role = aws_iam_role.lambda_exec.arn
  environment {
    variables = {
      PUBLIC_KEY = var.public_key
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Get IP IAMs
# first data sources
data "aws_ecs_cluster" "mc_cluster" {
  cluster_name = "minecraft_server"
}

data "aws_ecs_service" "mc_service" {
  service_name    = "minecraft_server"
  cluster_arn     = data.aws_ecs_cluster.mc_cluster.arn
}

data "aws_ecs_task_definition" "mc_td" {
  task_definition = aws_ecs_task_definition.minecraft-server-task-def.family
}

data "aws_ecs_task" "mc_task" {
  task_definition = data.aws_ecs_task_definition.mc_td.arn
}

data "aws_ec2_network_interface" "eni" {
  count = length(data.aws_ecs_task.mc_task.network_interfaces)
  id    = data.aws_ecs_task.mc_task.network_interfaces[count.index].id
}


# IAMS
data "aws_iam_policy_document" "lambda_get_ip" {
  statement {
    actions = [
      "ecs:ListTasks",
      "ecs:DescribeTasks"
    ]
    resources = [
      data.aws_ecs_cluster.mc_cluster.arn,
      data.aws_ecs_service.mc_service.arn,
      data.aws_ecs_task_definition.mc_td.arn
    ]
  }

  statement {
    actions = [
      "ec2:DescribeNetworkInterfaces"
    ]
    resources = [
      for eni in data.aws_ec2_network_interface.eni :
      "arn:aws:ec2:${var.region}:${data.aws_caller_identity.current.account_id}:network-interface/${eni.id}"
    ]
  }
}

resource "aws_iam_policy" "lambda_get_ip_policy" {
  name = "minecraft_lambda_get_ip_policy"
  policy = data.aws_iam_policy_document.lambda_get_ip.json
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_efs_role" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = aws_iam_policy.lambda_get_ip_policy.arn
}