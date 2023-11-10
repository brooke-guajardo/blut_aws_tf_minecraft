resource "aws_efs_file_system" "minecraft_efs" {}

resource "aws_efs_mount_target" "mount" {
  file_system_id = aws_efs_file_system.minecraft_efs.id
  subnet_id      = module.vpc.public_subnets
}

resource "aws_efs_mount_target" "minecraft_mounts" {
   count = "length(module.vpc.public_subnets)"
   file_system_id  = "${aws_efs_file_system.minecraft_efs.id}"
   subnet_id = "${element(module.vpc.public_subnets, count.index)}"
   security_groups = ["${aws_security_group.minecraft_sg.id}"]
}