variable "function_name" {
  type = string
}

variable "bucket_prefix" {
  type = string
}

variable "execution_rate" {
  type    = string
  default = "1 day"
}

variable "topic_name" {
  type    = string
  default = "uug-cs-vm-build-update-notify"
}