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
      version = "5.0.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4.0"
    }
  }
}
