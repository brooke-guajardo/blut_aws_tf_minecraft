resource "aws_security_group" "minecraft_sg" {
  name        = "minecraft_sg"
  description = "minecraft security group for ingress/egress"
  vpc_id      =  module.vpc.vpc_id
 
 # Using RCON player whitelist so not whitelisting CIDRs here, but wouldnt hurt to do tbh
  ingress {
    description = "rule for inbound access"
    from_port   = var.port
    to_port     = var.port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  egress {
    description = "rule for outbound access"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_security_group" "minecraft_efs_sg" {
  name        = "minecraft_efs_sg"
  description = "minecraft efs security group for ingress"
  vpc_id      =  module.vpc.vpc_id
 
 # ingress from ecs only to NFS port
  ingress {
    description = "rule for inbound efs access"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = module.vpc.public_subnets_cidr_blocks
  }
 
 # No egress needed for EFS

 depends_on = [aws_security_group.minecraft_sg]
}