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
      image         = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/minecraft:v8.0.0"
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
          value = "ConcentratedAndi,f_r_o_g_g_i_e,ElBigMacAttack,Jardo_Rook,NotL33tSauce"
        },
        {
          name = "EXISTING_WHITELIST_FILE"
          value = "SYNCHRONIZE"
        },
        {
          name = "MOTD"
          value = "No cover charge, 2 drink minimum."
        },
        {
          name = "SNOOPER_ENABLED"
          value = "FALSE"
        },
        {
          name = "CF_API_KEY"
          value = var.cf_api_key
        },
        {
          name = "CF_EXCLUDE_MODS"
          value = "structory,all-the-wizard-gear,towers-of-the-wild-modded"
        },
        {
          name = "ALLOW_FLIGHT"
          value = "TRUE"
        },
        {
          name = "CF_PAGE_URL"
          value = "https://www.curseforge.com/minecraft/modpacks/all-the-mods-9/files/4856145"
        }
      ]
      mountPoints   = [
        {
          containerPath = "/data"
          sourceVolume  = "minecraft-efs"
        }
      ]
    }
  ])
  volume {
    name      = "minecraft-efs"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.minecraft_efs.id
      root_directory = "/data"
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.minecraft_efs_ap.id
      }
    }
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