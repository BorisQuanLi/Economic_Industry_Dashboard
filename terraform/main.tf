provider "aws" {
  region = "us-east-1"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.28"
    }
  }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

locals {
  services = [
    "frontend",
    "fastapi_backend",
    "etl_service"
  ]
}

# ── VPC ──────────────────────────────────────────────────────────────────────

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "dashboard-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Project = "Economic_Industry_Dashboard" }
}

# ── ECR — one repo per service ────────────────────────────────────────────────

resource "aws_ecr_repository" "app_repos" {
  for_each             = toset(local.services)
  name                 = "dashboard/${each.key}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration { scan_on_push = true }
}

# ── RDS (private subnet) ──────────────────────────────────────────────────────

resource "aws_db_subnet_group" "db" {
  name       = "dashboard-db-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "db_sg" {
  name   = "dashboard-db-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "postgres" {
  identifier                          = "dashboard-db"
  allocated_storage                   = 20
  engine                              = "postgres"
  engine_version                      = "13"
  instance_class                      = "db.t3.micro"
  iam_database_authentication_enabled = true
  db_name                             = var.db_name
  username                            = var.db_user
  password                            = var.db_pass
  db_subnet_group_name                = aws_db_subnet_group.db.name
  vpc_security_group_ids              = [aws_security_group.db_sg.id]
  skip_final_snapshot                 = true
  publicly_accessible                 = false
}

# ── Secrets Manager — mirrors docker-compose env vars ────────────────────────

resource "aws_secretsmanager_secret" "db_secret" {
  name        = "dashboard-db-credentials"
  description = "PostgreSQL credentials for dashboard-db"
}

resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = var.db_user
    password = var.db_pass
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = var.db_name
  })
}

# ── IAM — EC2/ECS task role with RDS IAM auth ────────────────────────────────

resource "aws_iam_policy" "db_iam_auth" {
  name = "RDS_IAM_Auth_Policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = "rds-db:connect"
      Effect   = "Allow"
      Resource = "arn:aws:rds-db:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:..."
    }]
  })
}

resource "aws_iam_policy" "secrets_read" {
  name = "SecretsManager_Read_Policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["secretsmanager:GetSecretValue"]
      Effect   = "Allow"
      Resource = aws_secretsmanager_secret.db_secret.arn
    }]
  })
}

resource "aws_iam_role" "ecs_task_role" {
  name = "dashboard-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_rds" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.db_iam_auth.arn
}

resource "aws_iam_role_policy_attachment" "task_secrets" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.secrets_read.arn
}

# ECS needs a separate execution role to pull images and write logs
resource "aws_iam_role" "ecs_execution_role" {
  name = "dashboard-ecs-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "execution_managed" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ── ECS Cluster ───────────────────────────────────────────────────────────────

resource "aws_ecs_cluster" "main" {
  name = "dashboard-cluster"
}

# ── Security Groups ───────────────────────────────────────────────────────────

resource "aws_security_group" "ecs_sg" {
  name   = "dashboard-ecs-sg"
  vpc_id = module.vpc.vpc_id

  # FastAPI port — from ALB and within VPC
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "web_sg" {
  name   = "dashboard-frontend-sg"
  vpc_id = module.vpc.vpc_id

  # Streamlit public port
  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "frontend_sg" {
  name        = "frontend-access"
  description = "Allow access to Streamlit dashboard"
  vpc_id      = module.vpc.vpc_id

  # Inbound rule for the Streamlit UI
  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Change this to your IP if you want it private
  }

  # Standard outbound rule (needed for the container to pull images/data)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ── CloudWatch log group ──────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "dashboard" {
  name              = "/ecs/dashboard"
  retention_in_days = 7
}

# ── ECS Task: etl_service (one-shot, runs then exits) ────────────────────────
# Reuses the existing etl_service Docker image unchanged.
# DB_AUTH_MODE=iam triggers connection.py (Boto3 token) instead of password auth.

resource "aws_ecs_task_definition" "etl" {
  family                   = "dashboard-etl"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name    = "etl_service"
    image   = "${aws_ecr_repository.app_repos["etl_service"].repository_url}:latest"
    command = ["python", "etl_service/pipelines/standard_pipeline.py", "--init-db", "--companies-only"]
    environment = [
      { name = "DB_HOST", value = aws_db_instance.postgres.address },
      { name = "DB_NAME", value = var.db_name },
      { name = "DB_USER", value = "iam_user" },
      { name = "DB_AUTH_MODE", value = "iam" }, # activates connection.py IAM token path
      { name = "FMP_API_KEY", value = "YOUR_FMP_API_KEY" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.dashboard.name
        "awslogs-region"        = data.aws_region.current.id
        "awslogs-stream-prefix" = "etl"
      }
    }
  }])
}

# ── Internal ALB for fastapi_backend ─────────────────────────────────────────

resource "aws_lb" "fastapi" {
  name               = "dashboard-fastapi-alb"
  internal           = true
  load_balancer_type = "application"
  subnets            = module.vpc.private_subnets
  security_groups    = [aws_security_group.ecs_sg.id]
}

resource "aws_lb_target_group" "fastapi" {
  name        = "dashboard-fastapi-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_listener" "fastapi" {
  load_balancer_arn = aws_lb.fastapi.arn
  port              = 8000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }
}

# ── ECS Task: fastapi_backend (long-running service) ─────────────────────────

resource "aws_ecs_task_definition" "fastapi" {
  family                   = "dashboard-fastapi"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name         = "fastapi_backend"
    image        = "${aws_ecr_repository.app_repos["fastapi_backend"].repository_url}:latest"
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    environment = [
      { name = "DB_HOST", value = aws_db_instance.postgres.address },
      { name = "DB_NAME", value = var.db_name },
      { name = "DB_USER", value = var.db_user },
      { name = "DB_PASS", value = var.db_pass },
      { name = "REDIS_URL", value = "redis://localhost:6379/0" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.dashboard.name
        "awslogs-region"        = data.aws_region.current.id
        "awslogs-stream-prefix" = "fastapi"
      }
    }
  }])
}

resource "aws_ecs_service" "fastapi" {
  name            = "fastapi-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi.arn
    container_name   = "fastapi_backend"
    container_port   = 8000
  }
}

# ── ECS Task: frontend (Streamlit, public-facing) ────────────────────────────

resource "aws_ecs_task_definition" "frontend" {
  family                   = "dashboard-frontend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name         = "frontend"
    image        = "${aws_ecr_repository.app_repos["frontend"].repository_url}:latest"
    portMappings = [{ containerPort = 8501, protocol = "tcp" }]
    environment = [
      { name = "BACKEND_HOST", value = aws_lb.fastapi.dns_name },
      { name = "BACKEND_PORT", value = "8000" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.dashboard.name
        "awslogs-region"        = data.aws_region.current.id
        "awslogs-stream-prefix" = "frontend"
      }
    }
  }])
}

resource "aws_ecs_service" "frontend" {
  name            = "frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.public_subnets # public subnet → public IP
    security_groups  = [aws_security_group.web_sg.id]
    assign_public_ip = true # exposes :8501 at a public IP
  }
}

# ── Outputs ───────────────────────────────────────────────────────────────────

output "fastapi_alb_dns" {
  description = "Internal ALB DNS for fastapi_backend (used by frontend BACKEND_HOST)"
  value       = aws_lb.fastapi.dns_name
}

output "frontend_url" {
  description = "Streamlit dashboard — check ECS task ENI for the assigned public IP"
  value       = "http://<frontend-task-public-ip>:8501  (see ECS console → frontend service → task → ENI)"
}

output "ecr_urls" {
  description = "Push targets for docker build + push"
  value       = { for k, v in aws_ecr_repository.app_repos : k => v.repository_url }
}

output "rds_endpoint" {
  description = "RDS host for DB_HOST env var"
  value       = aws_db_instance.postgres.address
}
