provider "aws" {
  region = var.region
  default_tags {
    tags = {
      app = "minecraft"
    }
  }
}

terraform {
  required_version = "1.2.0"

  required_providers {
    aws      = {
      source = "hashicorp/aws"
      version = "4.67.0"
    }
  }
  # backend "s3" {
  #   bucket = "minecraft-tfstate"
  #   key = "prod"
  #   region = var.region
  # }
}
