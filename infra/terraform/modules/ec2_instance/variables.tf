variable "instance_name" {}
variable "ami_id" {}
variable "instance_type" {}
variable "subnet_id" {}
variable "vpc_security_group_ids" {
  type = list(string)
}
variable "key_name" {}
variable "user_data" {}