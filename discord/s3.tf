resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "blut-aws-tf-minecraft"
}

resource "aws_s3_bucket_ownership_controls" "lambda_bucket" {
  bucket = aws_s3_bucket.lambda_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "lambda_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.lambda_bucket]

  bucket = aws_s3_bucket.lambda_bucket.id
  acl    = "private"
}

resource "aws_s3_object" "lambda_load_python_artifact" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "deployment_package.zip"
  source = "${path.module}/deployment_package.zip"

  etag = filemd5("${path.module}/deployment_package.zip")
}
