variable "cpu" {
  description = "default amount of CPU to give to ecs"
  default = 4096
}

variable "memory" {
  description = "default amount of memory to give to ecs"
  default = 8192
}

variable "memory_env_var" {
  description = "default amount of memory to give to ecs, but this is set within the container"
  default = "8G"
}

variable "port" {
  description = "default container port"
  default = 25565
}

variable "region" {
  description = "default aws region"
  default = "us-east-1"
}

data "aws_caller_identity" "current" {}

variable "cf_api_key" {
  description = "api key from curseforge, provided during apply"
}