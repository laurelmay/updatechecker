resource "aws_sns_topic" "email_topic" {
  name = var.topic_name
}

resource "aws_sns_topic_policy" "read_policy" {
  arn = aws_sns_topic.email_topic.arn
  policy = templatefile("public-read.json", {
    topic         = aws_sns_topic.email_topic.arn,
    function_role = aws_iam_role.execution-role.arn
    }
  )
}
