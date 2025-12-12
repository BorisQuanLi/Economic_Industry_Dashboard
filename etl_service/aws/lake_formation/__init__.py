"""
AWS Lake Formation Integration Module

Provides Lake Formation setup, governance, and permissions management
for S3 data lake with Glue Catalog integration.
"""

from .setup import LakeFormationSetup

__all__ = ['LakeFormationSetup']
