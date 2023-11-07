data "aws_iam_policy_document" "mc_role_doc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
  statement {
    actions = [
        "s3:List*",
        "s3:Get*",
        "s3:Put*",
    ]

    resources = ["arn:aws:s3:::minecraft*"]
  }
}

resource "aws_iam_role" "ecs_tasks_execution_role" {
  name               = "ecs-task-execution-role"
  assume_role_policy = "${data.aws_iam_policy_document.mc_role_doc.json}"
}
