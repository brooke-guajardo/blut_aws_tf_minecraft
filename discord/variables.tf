data "aws_caller_identity" "current" {}

variable "region" {
  description = "default aws region"
  default = "us-east-1"
}

variable "public_key" {
  description = "pubkey of discord bot"
}

variable "rcon_pass" {
  description = "RCON password"
}