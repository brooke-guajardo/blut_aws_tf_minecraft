data "aws_secretsmanager_secret" "curseforge" {
  name = "/minecraft/curseforge"
}