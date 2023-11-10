variable "cpu" {
  description = "default amount of CPU to give to ecs"
  default = 4096
}

variable "memory" {
  description = "default amount of memory to give to ecs"
  default = 8192
}

variable "port" {
  description = "default container port"
  default = 25565
}

variable "region" {
  description = "default aws region"
  default = "us-east-1"
}