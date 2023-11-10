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
      image         = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/minecraft:latest"
      essential     = true
      tty           = true
      stdin_open    = true
      restart       = "unless-stopped"
      portMappings  = [
        {
          containerPort = var.port
          hostPort      = var.port
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
          value = "1.20.1"
        },
        {
          name = "TYPE"
          value = "AUTO_CURSEFORGE"
        },
        {
          name = "MEMORY"
          value = var.memory_env_var
        },
        {
          name = "WHITELIST"
          value = "ConcentratedAndi,f_r_o_g_g_i_e,ElBigMacAttack,Jardo_Rook"
        },
        {
          name = "MOTD"
          value = "No cover charge, 2 drink minimum."
        },
        {
          name = "CF_API_KEY"
          value = var.cf_api_key
        },
        {
          name = "CF_EXCLUDE_MODS"
          value = "snow-under-trees-remastered,fix-experience-bug,sparse-structures,structory-towers,structory,packet-fixer,all-the-wizard-gear,towers-of-the-wild-modded"
        },
        {
          name = "CF_PAGE_URL"
          value = "https://www.curseforge.com/minecraft/modpacks/all-the-mods-9"
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
    security_groups  = [aws_security_group.minecraft_sg.id]
    assign_public_ip = true
  }
  launch_type = "FARGATE"
}