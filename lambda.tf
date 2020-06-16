provider "aws" {
  profile = var.profile
  region  = var.region
}

data "aws_partition" "current" {}

resource "aws_s3_bucket" "storage" {
  bucket_prefix = var.bucket_prefix
}

resource "aws_iam_role" "execution-role" {
  name               = "update-checker-role"
  description        = "Allow downloading data to S3"
  assume_role_policy = file("lambda-assume-role.json")
  tags = {
    Service = "Lambda"
  }
}

resource "aws_iam_role_policy_attachment" "execution-attach" {
  role       = aws_iam_role.execution-role.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "check-function" {
  filename      = "lambda_function_payload.zip"
  function_name = var.function_name
  role          = aws_iam_role.execution-role.arn
  handler       = "lambda.handler"

  source_code_hash = filebase64sha256("lambda_function_payload.zip")

  runtime = "python3.8"
  timeout = 5

  environment {
    variables = {
      bucket      = aws_s3_bucket.storage.bucket
      email_topic = aws_sns_topic.email_topic.arn
    }
  }
}

resource "aws_cloudwatch_event_rule" "timer-event" {
  name        = "run-check-lambda"
  description = "Run version check Lambda every ${var.execution_rate}"

  schedule_expression = "rate(${var.execution_rate})"
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.check-function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.timer-event.arn
}

resource "aws_cloudwatch_event_target" "timer-target" {
  target_id = "run-lambda-every-day"
  arn       = aws_lambda_function.check-function.arn
  rule      = aws_cloudwatch_event_rule.timer-event.name
}

