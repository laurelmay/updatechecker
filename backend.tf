resource "aws_s3_bucket" "terraform_state" {
    bucket = "kylelaker-terraform-state"
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
    billing_mode = "PROVISIONED"
    read_capacity = 1
    write_capacity = 1
    hash_key = "LockID"

    attribute {
      name = "LockID"
      type = "S"
    }
}

terraform {
  backend "s3" {
      bucket = "kylelaker-terraform-state"
      key = "updatechecker/state"
      region = "us-east-1"

      dynamodb_table = "terraform-locks"
      encrypt = true
  }
}