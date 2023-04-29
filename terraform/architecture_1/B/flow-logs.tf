resource "aws_flow_log" "example" {
  log_destination      = aws_s3_bucket.logs-s3.arn
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.vpc.id
  max_aggregation_interval = 60
}

resource "aws_s3_bucket" "logs-s3" {
  bucket_prefix = "poc-"
  force_destroy = true
}

output "bucket" {
	value = "${aws_s3_bucket.logs-s3.id}"
}
