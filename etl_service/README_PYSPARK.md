# High-Throughput Analytics Pipeline (PySpark)

This service implements a distributed data processing engine using the PySpark DataFrame API. It demonstrates enterprise-grade patterns for large-scale data transformation, enrichment, and quality assurance.

## Core Engineering Patterns Demonstrated


| Technical Pattern | Implementation Detail | Business Logic Context |
|:---|:---|:---|
| **Window Functions** | `rank().over(...)` | Multi-dimensional risk ranking |
| **Time-Series Delta** | `lag()` for sequential trends | Performance & growth velocity |
| **Relational Enrichment** | Broadcast & Left Joins | Entity-level metadata augmentation |
| **Aggregations** | `groupBy` + `agg()` | Sector-level summary statistics |
| **Logic Branching** | Outlier detection flagging | Complex conditional categorization |
| **Optimization** | `.cache()` & DAG management | Reducing re-computation overhead |

## Quick Start

```bash
# Automated Setup (Root Directory)
make setup

# Manual Component Execution
cd etl_service/
python -m pipelines.spark_pipeline
pytest tests/test_spark_companies_builder.py -v
