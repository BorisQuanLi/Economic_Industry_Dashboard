"""
Setup script for the Economic Industry Dashboard package.
"""
from setuptools import setup, find_packages

setup(
    name="economic_industry_dashboard",
    version="0.1.0",
    description="Financial analytics dashboard for S&P 500 companies",
    author="Economic Industry Dashboard Team",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "pandas>=1.3.0",
        "psycopg2-binary>=2.9.0",
        "numpy>=1.20.0",
        "simplejson>=3.17.0",
        "requests>=2.25.0",
        "pytest>=6.2.0",
        "streamlit>=1.0.0",
        "matplotlib>=3.4.0",
        "openpyxl>=3.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
