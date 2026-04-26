# Terraform — AWS Deployment

Deploys the Economic Industry Dashboard stack to AWS: three ECS Fargate services (`frontend`, `fastapi_backend`, `etl_service`), a private RDS PostgreSQL instance, ECR image repositories, and a VPC with public/private subnets.

---

## Quick Start

### Prerequisites
- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.5
- AWS CLI configured (`aws configure`) with permissions for ECS, ECR, RDS, IAM, VPC, and Secrets Manager
- Docker

### 1. Initialize Terraform

```bash
cd terraform/
terraform init
```

### 2. Set credentials

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — set db_user, db_pass, db_name
```

### 3. Create infrastructure and ECR repositories

```bash
terraform apply
```

Note the `ecr_urls` output — you'll need these in the next step.

### 4. Build and push Docker images
Navigate back to the project root (one level up from `terraform/`) so Docker can find the service folders:

```bash
cd ..

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1
ECR_BASE="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_BASE

# Build and Push
for SERVICE in frontend fastapi_backend etl_service; do
    docker build -t $ECR_BASE/dashboard/$SERVICE:latest ./$SERVICE
    docker push $ECR_BASE/dashboard/$SERVICE:latest
done

# Trigger ECS to pull the new images
aws ecs update-service --cluster dashboard-cluster --service frontend --force-new-deployment
aws ecs update-service --cluster dashboard-cluster --service fastapi-backend --force-new-deployment
```

### 5. Create the RDS IAM user

Connect to RDS once using the master password (from `terraform.tfvars`), then:

```sql
CREATE USER iam_user WITH LOGIN;
GRANT rds_iam TO iam_user;
```

### 6. Open the dashboard

ECS assigns a public IP to the frontend task. To find it:

```bash
aws ecs list-tasks --cluster dashboard-cluster --service-name frontend
aws ecs describe-tasks --cluster dashboard-cluster --tasks <task-arn> \
  --query 'tasks[0].attachments[0].details'
# Look for the "networkInterfaceId" value, then:
aws ec2 describe-network-interfaces --network-interface-ids <eni-id> \
  --query 'NetworkInterfaces[0].Association.PublicIp' --output text
```

Open `http://<public-ip>:8501` in your browser.

### 7. Tear down when done

> ⚠️ RDS, NAT Gateway, and ECS Fargate incur ongoing costs. Destroy the stack when you are finished.

```bash
terraform destroy
```

---

## Architecture

```
Internet
    │
    ▼ :8501
ECS Fargate — frontend          (public subnet, public IP)
    │
    ▼ :8000
ECS Fargate — fastapi_backend   (private subnet)
    │
    ▼ :5432
RDS PostgreSQL                  (private subnet, IAM auth)
    ▲
ECS Fargate — etl_service       (private subnet, one-shot on deploy)
```

## IAM Authentication

EC2/ECS tasks connect to RDS using short-lived IAM tokens (15 min) instead of static passwords. This is handled by `etl_service/src/db/connection.py` and activated by the `DB_AUTH_MODE=iam` environment variable set in the task definitions.
