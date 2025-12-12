"""
AWS Glue Integration Module

Provides AWS Glue job scripts and catalog management for serverless ETL processing.
"""

from .glue_job import GlueS3ETLPipeline, main

__all__ = ['GlueS3ETLPipeline', 'main']
