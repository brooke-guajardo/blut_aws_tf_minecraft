resource "aws_ecs_cluster" "minecraft_server" {
  name = "minecraft_server"
}

resource "aws_ecs_task_definition" "minecraft_server" {
  cpu                      = var.cpu
  memory                   = var.memory
  family                   = "minecraft-server-task-def"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  container_definitions = jsonencode([
    {
      name          = "minecraft-server"
      image         = "itzg/minecraft-server:latest"
      essential     = true
      portMappings  = [
        {
          containerPort = 25565
          hostPort      = 25565
          protocol      = "tcp"
        }
      ]
      environment   = [
        {
          name  = "EULA"
          value = "TRUE"
        },
        {
          name = "VERSION"
          value = "1.19.2"
        },
        {
          name = "TYPE"
          value = "AUTO_CURSEFORGE"
        },
        {
          name = "CF_API_KEY"
          value = data.aws_secretsmanager_secret.curseforge.arn # this isnt the secret value
        },
        {
          name = "CF_PAGE_URL"
          value = "https://www.curseforge.com/minecraft/modpacks/all-the-mods-8"
        }
      ]
      mountPoints   = [
        {
          containerPath = "/data"
          sourceVolume  = "minecraft-data"
        }
      ]
    }
  ])
  volume {
    name = "minecraft-data"
  }
}

resource "aws_ecs_service" "minecraft_server" {
  name            = "minecraft_server"
  cluster         = aws_ecs_cluster.minecraft_server.id
  task_definition = aws_ecs_task_definition.minecraft_server.arn
  desired_count   = 1
  network_configuration {
    subnets          = module.vpc.public_subnets
    security_groups  = [aws_security_group.minecraft_server.id]
    assign_public_ip = true
  }
  launch_type = "FARGATE"
}