resource "aws_ecr_repository" "minecraft_images" {
  name                 = "minecraft"
  image_tag_mutability = "IMMUTABLE"
}

resource "aws_ecr_repository" "discord_lambda" {
  name                 = "discord-lambda"
  image_tag_mutability = "IMMUTABLE"
}