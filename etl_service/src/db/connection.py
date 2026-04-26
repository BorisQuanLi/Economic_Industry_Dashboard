"""
IAM token-based RDS connection for EC2/ECS deployments.
Activated when DB_AUTH_MODE=iam is set in the environment.
Replaces the static-password psycopg2.connect() call in db.py.
"""
import boto3
import psycopg2
from etl_service.settings import DB_HOST, DB_NAME, DB_USER

def get_iam_token_connection():
    """Generate a 15-minute Boto3 auth token and open a psycopg2 connection to RDS."""
    client = boto3.client("rds")
    token = client.generate_db_auth_token(
        DBHostname=DB_HOST,
        Port=5432,
        DBUsername=DB_USER,  # must match the IAM policy Resource ARN dbuser segment
    )
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=token,
        sslmode="require",  # RDS IAM auth requires SSL
    )
