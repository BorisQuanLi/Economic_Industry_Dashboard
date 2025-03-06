import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    DB_URI: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    REDSHIFT_URI: str
    S3_BUCKET: str
    ENV: str

def load_config(env: str = 'dev') -> Config:
    """Load configuration based on environment"""
    return Config(
        DB_URI=os.getenv('DB_URI', 'postgresql://localhost/sp500'),
        AWS_ACCESS_KEY=os.getenv('AWS_ACCESS_KEY'),
        AWS_SECRET_KEY=os.getenv('AWS_SECRET_KEY'),
        REDSHIFT_URI=os.getenv('REDSHIFT_URI'),
        S3_BUCKET=os.getenv('S3_BUCKET', 'sp500-financial-data'),
        ENV=env
    )
