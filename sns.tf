resource "aws_sns_topic" "email_topic" {
  name = var.topic_name
}

resource "aws_sns_topic_policy" "read_policy" {
  arn = aws_sns_topic.email_topic.arn
  policy = templatefile("public-read.json", {
    topic    = aws_sns_topic.email_topic.arn,
    function = aws_lambda_function.check-function
    }
  )
}

resource "aws_iam_role_policy" "policy" {
  name = "s3-sns-access"
  role = aws_iam_role.execution-role.id

  policy = templatefile("lambda-role-policy.json", {
    bucket = aws_s3_bucket.storage.arn
    topic  = aws_sns_topic.email_topic.arn
    }
  )
}