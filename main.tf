provider "aws" {
  region = "us-east-1"
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
  backend "s3" {}
}
