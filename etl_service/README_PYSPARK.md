# PySpark ETL — Financial Crimes / AML Analytics

PySpark-powered ETL pipeline for S&P 500 data, demonstrating the DataFrame API
skills required for enterprise Financial Crimes and AML engineering roles.

## PySpark Skills Demonstrated

| Skill | Where |
|---|---|
| Window functions — `rank().over(Window.partitionBy(...))` | `SparkCompaniesBuilder.get_transaction_risk_summary` |
| Window functions — `lag()` for sequential delta / velocity | `SparkCompaniesBuilder.get_sector_growth_trend` |
| Explicit `groupBy` + `agg(count(), avg())` | `SparkCompaniesBuilder.get_sector_summary` |
| DataFrame `join` (left join, sector risk enrichment) | `SparkCompaniesBuilder.join_sector_risk_profile` |
| Filtering logic + AML outlier flagging | `SparkCompaniesBuilder.run_analysis` |
| `.cache()` to avoid DAG re-computation | `SparkCompaniesBuilder.run` |
| Multi-step `.select` / `.withColumn` transformation chain | `SparkCompaniesBuilder.transform_companies_data` |
| Data quality filtering | `SparkCompaniesBuilder._add_data_quality_checks` |

## Quick Start

```bash
cd etl_service/
source venv/bin/activate

# Run full AML analytics demo (window functions, join, lag, AML flags)
python -m pipelines.spark_pipeline

# Run tests
pytest tests/test_spark_companies_builder.py -v
```

## Key Modules

- `src/adapters/spark_companies_builder.py` — core PySpark logic
- `pipelines/spark_pipeline.py` — end-to-end demo runner
- `tests/test_spark_companies_builder.py` — unit tests for all analytics methods

## AML / Financial Crimes Context

`get_sector_summary` flags sectors where `avg_employees > 50,000` as
`"High Capacity / Review Needed"` — a proxy for the kind of outlier detection
used in AML transaction monitoring pipelines.

`get_sector_growth_trend` uses `lag()` to compute employee count deltas ordered
by founding year within each sector — analogous to transaction velocity checks
used in financial crimes detection.

`join_sector_risk_profile` enriches each company row with its sector's aggregate
risk flag via a Spark DataFrame join, mirroring how entity-level data is enriched
with reference/risk tables in AML pipelines.

## Prerequisites

```bash
java -version  # Java 8+ required
python -c "import pyspark; print(pyspark.__version__)"
```
