variable "db_name" {
  description = "Database name"
  type        = string
  default     = "investment_analysis"
}

variable "db_user" {
  description = "Database admin username"
  type        = string
  sensitive   = true
}

variable "db_pass" {
  description = "Database admin password"
  type        = string
  sensitive   = true
}

variable "aws_secrets" {
  description = "Configuration for AWS Secrets Manager"
  type = object({
    name        = string
    description = string
  })
  default = {
    name        = "dashboard-db-credentials"
    description = "Database credentials"
  }
}

