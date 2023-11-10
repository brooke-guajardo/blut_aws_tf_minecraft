resource "aws_efs_file_system" "minecraft_efs" {}

resource "aws_efs_mount_target" "mount" {
  file_system_id = aws_efs_file_system.minecraft_efs.id
  subnet_id      = module.vpc.public_subnets
}

resource "aws_efs_mount_target" "minecraft_mount_1" {
   file_system_id  = aws_efs_file_system.minecraft_efs.id
   subnet_id = module.vpc.public_subnets[0]
   security_groups = data.aws_security_group.minecraft_sg.id
}