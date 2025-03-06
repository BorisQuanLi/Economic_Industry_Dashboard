import os

class Config:
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DEBUG = os.getenv('DEBUG', True)
    TESTING = os.getenv('TESTING', False)

class DevelopmentConfig(Config):
    DB_NAME = 'sp500_financial_analytics_dev'

class TestingConfig(Config):
    DB_NAME = 'sp500_financial_analytics_test'
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    DB_NAME = 'sp500_financial_analytics'
