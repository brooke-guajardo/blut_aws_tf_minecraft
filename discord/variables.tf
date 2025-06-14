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

variable "discord_app_id" {
  description = "Discord bots APPLICATION ID"
}

variable "discord_lambda_image_tag" {
  description = "Container image tag for the discord lambda"
  type        = string
  default     = "latest"
}