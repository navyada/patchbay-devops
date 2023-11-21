resource "aws_s3_bucket" "app_public_files" {
  bucket        = "${local.prefix}-files-${data.aws_caller_identity.current.account_id}"
  acl           = "public-read"
  force_destroy = true
}