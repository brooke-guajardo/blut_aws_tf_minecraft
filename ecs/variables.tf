data "aws_caller_identity" "current" {}

variable "cpu" {
  description = "default amount of CPU to give to ecs"
  default = 8192
}

##########################
#### Change these together
##########################

variable "memory" {
  description = "default amount of memory to give to ecs"
  default = 32768
}

variable "memory_env_var" {
  description = "default amount of memory to give to ecs, but this is set within the container"
  default = "32G"
}

##########################
##########################
##########################

variable "port" {
  description = "default container port for image, don't change unless you know what you're doing. This is the default minecraft port"
  default = 25565
}

variable "region" {
  description = "default aws region"
  default = "us-east-1"
}

variable "cf_api_key" {
  description = "api key from curseforge, provided during apply"
}