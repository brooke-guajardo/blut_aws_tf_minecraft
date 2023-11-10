resource "aws_efs_file_system" "minecraft_efs" {
    creation_token = "minecraft"
}

resource "aws_efs_mount_target" "minecraft_mount_1" {
   file_system_id  = aws_efs_file_system.minecraft_efs.id
   subnet_id = module.vpc.public_subnets[0]
   security_groups = [aws_security_group.minecraft_efs_sg.id]
}

resource "aws_efs_mount_target" "minecraft_mount_2" {
   file_system_id  = aws_efs_file_system.minecraft_efs.id
   subnet_id = module.vpc.public_subnets[1]
   security_groups = [aws_security_group.minecraft_efs_sg.id]
}

resource "aws_efs_mount_target" "minecraft_mount_3" {
   file_system_id  = aws_efs_file_system.minecraft_efs.id
   subnet_id = module.vpc.public_subnets[2]
   security_groups = [aws_security_group.minecraft_efs_sg.id]
}