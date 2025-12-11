# PySpark ETL Implementation

This directory contains PySpark-enabled ETL pipeline components for distributed processing of S&P 500 financial data.

## 🚀 Quick Start

### 1. Test PySpark Setup
```bash
cd etl_service/
source venv/bin/activate
python test_pyspark.py
```

### 2. Run PySpark ETL Pipeline
```bash
# Local mode (single machine)
python run_pipeline.py --spark-mode local --companies-only

# Local mode with all CPU cores
python run_pipeline.py --spark-mode "local[*]" --companies-only

# Using dedicated PySpark runner
python run_pipeline_spark.py --spark-mode local --companies-only
```

## 📁 PySpark Components

### Core Files
- **`run_pipeline_spark.py`** - Main PySpark ETL pipeline runner
- **`src/adapters/spark_companies_builder.py`** - PySpark-based companies data processor
- **`aws_glue_job.py`** - AWS Glue job script for serverless execution
- **`test_pyspark.py`** - Setup verification and integration tests

### Key Features
- **Distributed Processing** - Leverage Spark's distributed computing capabilities
- **Data Quality Checks** - Built-in validation and cleansing
- **Multiple Output Formats** - Support for PostgreSQL, S3, Parquet
- **AWS Integration** - Ready for Glue, EMR, and ECS deployment

## 🔧 Local Development

### Prerequisites
```bash
# Ensure Java 8+ is installed (required for Spark)
java -version

# Activate virtual environment
source venv/bin/activate

# Verify PySpark installation
python -c "import pyspark; print(pyspark.__version__)"
```

### Running Tests
```bash
# Test basic PySpark functionality
python test_pyspark.py

# Test with existing Wikipedia integration
python -c "from etl_service.src.adapters.spark_companies_builder import SparkCompaniesBuilder; print('✅ Import successful')"
```

### Development Workflow
1. **Local Testing** - Use `local[*]` mode for development
2. **Data Validation** - Run quality checks on sample data
3. **Performance Tuning** - Optimize Spark configurations
4. **AWS Preparation** - Test with Glue job script

## ☁️ AWS Deployment Options

### 1. AWS Glue (Recommended)
```bash
# Upload Glue job script
aws s3 cp aws_glue_job.py s3://your-glue-scripts-bucket/

# Create Glue job
aws glue create-job \
  --name "sp500-etl-pipeline" \
  --role "GlueServiceRole" \
  --command '{"Name":"glueetl","ScriptLocation":"s3://your-glue-scripts-bucket/aws_glue_job.py"}'
```

### 2. Amazon EMR
- Deploy PySpark jobs on managed Hadoop clusters
- Suitable for large-scale data processing
- Cost-effective for batch processing

### 3. ECS with Spark
- Containerized Spark applications
- Integration with existing ECS infrastructure
- Custom resource allocation

## 📊 Performance Considerations

### Spark Configuration
```python
spark = SparkSession.builder \
    .appName("S&P500-ETL") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()
```

### Memory Optimization
- **Driver Memory**: 2-4GB for metadata operations
- **Executor Memory**: Scale based on data volume
- **Partitioning**: Optimize for data locality

### Data Processing Patterns
- **Extract**: Parallel data ingestion from multiple sources
- **Transform**: Distributed data cleansing and enrichment
- **Load**: Bulk writes to PostgreSQL and S3

## 🔍 Monitoring & Debugging

### Spark UI
- Access at `http://localhost:4040` during local execution
- Monitor job progress, stages, and resource utilization

### Logging
```python
# Enable detailed logging
spark.sparkContext.setLogLevel("INFO")

# Custom application logging
import logging
logger = logging.getLogger(__name__)
logger.info("Processing batch...")
```

### Common Issues
1. **Java Version** - Ensure Java 8+ compatibility
2. **Memory Errors** - Increase driver/executor memory
3. **Serialization** - Use Kryo serializer for performance
4. **Network** - Configure cluster networking for distributed mode

## 🎯 Investment Banking Use Cases

### Real-time Analytics
- Process streaming financial data
- Calculate risk metrics across portfolios
- Generate compliance reports

### Batch Processing
- End-of-day settlement processing
- Historical data analysis
- Regulatory reporting

### Data Lake Integration
- Ingest from multiple data sources
- Transform for analytics workloads
- Support for various file formats (Parquet, Delta, etc.)

## 📈 Next Steps

1. **Scale Testing** - Test with larger datasets
2. **AWS Integration** - Deploy to Glue/EMR
3. **Streaming** - Add Spark Streaming capabilities
4. **ML Integration** - Connect with MLlib for predictive analytics
5. **Delta Lake** - Implement ACID transactions for data lake

## 🔗 Related Documentation
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/)
- [PySpark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)