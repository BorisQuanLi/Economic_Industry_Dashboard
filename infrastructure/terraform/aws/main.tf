provider "aws" {
  region = var.aws_region
}

module "s3" {
  source = "./modules/s3"
  environment = var.environment
}

module "redshift" {
  source = "./modules/redshift"
  environment = var.environment
}

module "eks" {
  source = "./modules/eks"
  environment = var.environment
}
