provider "aws" {
  region = "us-east-1" # Change this to your preferred region
}

locals {
  services = [
    "frontend",
    "fastapi_backend",
    "etl_service",
    "kotlin-data-agent",
    "airflow"
  ]
}

resource "aws_ecr_repository" "app_repos" {
  for_each             = toset(local.services)
  name                 = "dashboard/${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_db_subnet_group" "db" {
  name       = "dashboard-db-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "db_sg" {
  name   = "dashboard-db-sg"
  vpc_id = module.vpc.vpc_id

  # Allow access from within the VPC (your backend services)
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}

# 1. Create the Secret container
resource "aws_secretsmanager_secret" "db_secret" {
  name        = "dashboard-db-credentials"
  description = "PostgreSQL credentials for dashboard-db"
}

# 2. Create the Secret Version (the actual JSON data)
resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = var.db_user
    password = var.db_pass
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
  })
}

# 3. DB instance variables
resource "aws_db_instance" "postgres" {
  identifier           = "dashboard-db"
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "13"
  instance_class       = "db.t3.micro" # Free tier eligible
  db_name              = var.db_name
  username             = var.db_user
  password             = var.db_pass # Initial password set from variable
  db_subnet_group_name = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  skip_final_snapshot  = true
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "dashboard-vpc"
  cidr = "10.0.0.0/16"

  # Spread across two availability zones for high availability
  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true # Keeps costs down for development
  
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Project = "Economic_Industry_Dashboard"
  }
}
