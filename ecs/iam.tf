data "aws_iam_policy_document" "ecs_tasks_execution_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_tasks_execution_role" {
  name               = "ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_execution_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_execution_role" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}



# EFS Stuff
data "aws_iam_policy_document" "ecs_task_efs" {
  statement {
    actions = ["elasticfilesystem:ClientWrite"]

  resources = [
    data.aws_efs_file_system.minecraft_efs.arn
  ]
  }
}

resource "aws_iam_policy" "ecs_task_efs_policy" {
  name = "minecraft_ecs_task_efs_policy"
  policy = data.aws_iam_policy_document.ecs_task_efs.json
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_efs_role" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = data.aws_iam_policy.ecs_task_efs_policy.arn
}