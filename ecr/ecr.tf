resource "aws_ecr_repository" "minecraft_images" {
  name                 = "minecraft"
  image_tag_mutability = "IMMUTABLE"
}