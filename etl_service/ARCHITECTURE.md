# ETL Service Architecture

## Overview

The ETL service is modularized by AWS service and functional responsibility to support enterprise-scale data pipeline operations. This architecture aligns with JPMC's tech stack requirements: **PySpark**, **AWS ECS**, **AWS Glue**, **Lake Formation**, and **Snowflake**.

## Directory Structure

```
etl_service/
├── aws/                          # AWS service integrations
│   ├── glue/                     # AWS Glue serverless ETL
│   │   ├── __init__.py
│   │   └── glue_job.py          # Glue job script for distributed processing
│   ├── lake_formation/           # AWS Lake Formation data governance
│   │   ├── __init__.py
│   │   └── setup.py             # Lake Formation setup and permissions
│   └── s3/                       # S3 data lake operations
│       └── __init__.py
│
├── pipelines/                    # ETL pipeline orchestration
│   ├── __init__.py
│   ├── spark_pipeline.py        # PySpark-based ETL pipeline
│   ├── standard_pipeline.py     # Standard Python ETL pipeline
│   └── lake_formation_pipeline.py  # PySpark + Lake Formation integration
│
├── src/                          # Core business logic
│   ├── adapters/                 # Data extraction adapters
│   ├── db/                       # Database connections and migrations
│   └── models/                   # Data models and queries
│
└── tests/                        # Consolidated test suite
    ├── __init__.py
    └── test_pyspark.py          # PySpark functionality tests
```

## Module Responsibilities

### `aws/` - AWS Service Integrations

Organized by AWS service to demonstrate clear understanding of cloud architecture:

#### `aws/glue/`
- **Purpose**: Serverless ETL execution using AWS Glue
- **Key Components**:
  - `glue_job.py`: AWS Glue job script with DynamicFrame transformations
  - Glue Data Catalog integration
  - Data quality checks
  - S3 and RDS connectivity

#### `aws/lake_formation/`
- **Purpose**: Data lake governance and access control
- **Key Components**:
  - `setup.py`: Lake Formation infrastructure setup
  - S3 bucket registration
  - Glue Catalog database creation
  - Permission management

#### `aws/s3/`
- **Purpose**: S3 data lake operations (future expansion)
- **Planned Features**:
  - Data lake folder structure management
  - S3 lifecycle policies
  - Cross-region replication

### `pipelines/` - ETL Orchestration

Different pipeline execution modes for various use cases:

#### `spark_pipeline.py`
- **Purpose**: PySpark-based distributed data processing
- **Features**:
  - Spark session management with PostgreSQL JDBC
  - DataFrame transformations
  - Adaptive query execution
  - Local and cluster execution modes

#### `lake_formation_pipeline.py`
- **Purpose**: PySpark + Lake Formation integration
- **Features**:
  - S3 data lake extraction
  - PySpark transformations
  - Glue Catalog registration
  - Snowflake export capability

#### `standard_pipeline.py`
- **Purpose**: Traditional Python ETL for smaller datasets
- **Features**:
  - Direct database operations
  - Wikipedia data extraction
  - Pandas-based transformations

### `src/` - Core Business Logic

Existing well-structured modules (unchanged):

- **`adapters/`**: Data source adapters (Wikipedia, Spark builders)
- **`db/`**: Database connections and SQL migrations
- **`models/`**: Data models, queries, and aggregations

### `tests/` - Test Suite

Consolidated testing for all components:

- **`test_pyspark.py`**: PySpark functionality verification
- Future: `test_glue.py`, `test_lake_formation.py`

## Import Patterns

### Before Modularization
```python
from etl_service import aws_glue_job
from etl_service import aws_lake_formation_setup
from etl_service import run_pipeline_spark
```

### After Modularization
```python
from etl_service.aws.glue import GlueS3ETLPipeline
from etl_service.aws.lake_formation import LakeFormationSetup
from etl_service.pipelines import SparkETLPipeline, PySparkLakeFormationETL
```

## JPMC Tech Stack Alignment

This architecture demonstrates proficiency in the required technologies:

### ✅ Python/PySpark
- `pipelines/spark_pipeline.py`: Distributed data processing
- `pipelines/lake_formation_pipeline.py`: PySpark + AWS integration
- `src/adapters/spark_companies_builder.py`: Spark DataFrame operations

### ✅ AWS ECS (Container-Ready)
- All modules are containerized via `Dockerfile`
- Stateless design for Fargate deployment
- Environment-based configuration

### ✅ AWS Glue
- `aws/glue/glue_job.py`: Serverless ETL job script
- Glue Data Catalog integration
- DynamicFrame transformations

### ✅ Lake Formation
- `aws/lake_formation/setup.py`: Data governance setup
- S3 data lake registration
- Fine-grained access control

### ✅ Snowflake Integration
- `pipelines/lake_formation_pipeline.py`: Snowflake export logic
- Data warehouse connectivity prepared

## Execution Examples

### Run PySpark Pipeline
```bash
python -m etl_service.pipelines.spark_pipeline --spark-mode local[*]
```

### Run Lake Formation Pipeline
```bash
python -m etl_service.pipelines.lake_formation_pipeline
```

### Setup Lake Formation
```bash
python -m etl_service.aws.lake_formation.setup
```

### Run AWS Glue Job (on AWS)
```bash
aws glue start-job-run --job-name sp500-etl-job
```

## Design Principles

1. **Separation of Concerns**: AWS services, pipelines, and business logic are clearly separated
2. **Scalability**: Easy to add new AWS services or pipeline types
3. **Enterprise-Ready**: Follows microservices architecture patterns
4. **Interview-Friendly**: Clear structure for code review and discussion
5. **Production-Grade**: Proper module organization and documentation

## Future Enhancements

- [ ] Add `aws/s3/data_lake.py` for S3 operations
- [ ] Create `pipelines/base_pipeline.py` abstract base class
- [ ] Expand test coverage in `tests/`
- [ ] Add `aws/ecs/` module for ECS task management
- [ ] Implement `aws/rds/` module for database operations

## References

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [AWS Lake Formation Documentation](https://docs.aws.amazon.com/lake-formation/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
