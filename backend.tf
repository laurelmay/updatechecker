resource "aws_s3_bucket" "terraform_state" {
    bucket_prefix = "terraform_state"
    versioning {
      enabled = true
    }
    server_side_encryption_configuration {
      rule {
          apply_server_side_encryption_by_default {
              sse_algorithm = "AES256"
          }
      }
    }
}

resource "aws_dynamodb_table" "terraform_locks" {
    name = "terraform-locks"
}

terraform {
  backend "s3" {
      bucket = aws_s3_bucket.terraform_state
      key = "updatechecker/state"
      region = var.region

      dynamodb_table = aws_dynamodb_table.terraform_locks.topic_name
      encrypt = true
  }
}