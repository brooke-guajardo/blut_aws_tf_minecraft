resource "aws_lambda_function" "blut_aws_tf_minecraft_lambda" {
  function_name = "blut_aws_tf_minecraft_lambda"

  package_type = "Image"
  image_uri    = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/discord-lambda:${var.discord_lambda_image_tag}"

  timeout = 120

  role = aws_iam_role.lambda_exec.arn
  environment {
    variables = {
      PUBLIC_KEY = var.public_key
      RCON_PASSWORD = var.rcon_pass
      DISCORD_APP_ID = var.discord_app_id
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
data "aws_iam_policy_document" "lambda_get_ip" {
  statement {
    actions = [
      "ecs:ListTasks",
      "ecs:DescribeTasks"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    actions = [
      "ec2:DescribeNetworkInterfaces"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    actions = [
      "ecs:UpdateService"
    ]
    resources = [
      data.terraform_remote_state.local_ecs.outputs.minecraft_ecs_arn
    ]
  }
}

resource "aws_iam_policy" "lambda_get_ip_policy" {
  name = "minecraft_lambda_get_ip_policy"
  policy = data.aws_iam_policy_document.lambda_get_ip.json
}

resource "aws_iam_role_policy_attachment" "lambda_get_ip_role" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_get_ip_policy.arn
}