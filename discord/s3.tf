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

data "archive_file" "lambda_load_python_artifact" {
  type = "zip"

  source_dir  = "${path.module}/deployment_package.zip"
  output_path = "${path.module}/deployment_package.zip"
}

resource "aws_s3_object" "lambda_load_python_artifact" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "deployment_package.zip"
  source = data.archive_file.lambda_load_python_artifact.output_path

  etag = filemd5(data.archive_file.lambda_load_python_artifact.output_path)
}
