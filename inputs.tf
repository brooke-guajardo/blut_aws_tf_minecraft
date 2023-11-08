data "aws_secretsmanager_secret" "curseforge" {
  name = "/minecraft/curseforge"
}

data "aws_kms_alias" "curseforge" {
  name = "alias/aws/secretsmanager"
}