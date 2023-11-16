resource "aws_efs_file_system" "minecraft_efs" {
    creation_token = "minecraft"
}

resource "aws_efs_access_point" "minecraft_efs_ap" {
  file_system_id = aws_efs_file_system.minecraft_efs.id
  
  # itzg/minecraft-server defaults to gid/uid: 1000
  posix_user {
    gid = 1000 
    uid = 1000
  }
  root_directory {
    path = "/data"
    creation_info {
      owner_gid = 1000
      owner_uid = 1000
      permissions = 755
    }
  }
}

resource "aws_efs_mount_target" "minecraft_mount" {
  count            = length(module.vpc.public_subnets)
  file_system_id   = aws_efs_file_system.minecraft_efs.id
  subnet_id        = module.vpc.public_subnets[count.index]
  security_groups  = [aws_security_group.minecraft_efs_sg.id]
}