resource "aws_s3_bucket" "app_public_files" {
  bucket_prefix = "${local.prefix}-files"
  acl           = "public-read"
  force_destroy = true
}
