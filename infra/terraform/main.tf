provider "aws" {
  region = var.region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "monitoring-vpc"
  cidr   = "10.0.0.0/16"

  azs             = ["${var.region}a"]
  public_subnets  = ["10.0.1.0/24"]
  enable_dns_hostnames = true

  tags = {
    Project = "SRE Monitoring"
  }
}

module "security_group" {
  source = "terraform-aws-modules/security-group/aws"
  name   = "monitoring-sg"
  vpc_id = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = "199.119.233.173/32"
    },
    {
      from_port   = 5001
      to_port     = 5001
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 8086
      to_port     = 8086
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 3000
      to_port     = 3000
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = {
    Project = "SRE Monitoring"
  }
}

module "ec2" {
  source = "./modules/ec2_instance/"

  instance_name          = "monitoring-node"
  ami_id                 = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = [module.security_group.security_group_id]
  key_name               = var.key_name
  user_data              = file("user_data.sh")
}