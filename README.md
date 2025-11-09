
### Description

**Enterprise Financial Data Pipeline** - A three-stage modernization showcasing Wall Street-grade data engineering:

🏗️ **STAGE 1 COMPLETE**: Flask Backend Refactoring with Blueprint Architecture  
🚀 **STAGE 2 COMPLETE**: Airflow ETL Automation with Sliding Window Algorithm  
✅ **STAGE 3 COMPLETE**: FastAPI High-Performance API Layer  

This project demonstrates enterprise-grade financial data processing through a complete modernization journey: Flask → Airflow → FastAPI, addressing real-world investment banking automation challenges, including Apple's disparate Q4 filing dates vs industry peers. The system processes S&P 500 financial statements with rate-limited API integration, stores data in PostgreSQL, and provides both Flask and FastAPI endpoints for financial analytics.

**Key Innovation**: Sliding window algorithm enabling accurate cross-sector analysis despite disparate corporate filing schedules.

**Stage 1: Flask Backend (Complete)**
Modular S&P 500 financial data ingestion with PostgreSQL storage, MVC patterns, and comprehensive testing framework.

**Stage 2: Airflow Automation (Complete)**
Enterprise ETL pipeline with rate-limited Financial Modeling Prep API integration, processing all 11 S&P sectors with automated data quality checks.

**Stage 3: FastAPI Implementation (Complete)**
High-performance async endpoints featuring sliding window algorithm that solves Apple Q4 (October) vs industry Q4 (December) filing disparities for accurate cross-sector investment analysis.

**Stage 4: MCP Multi-Agent System (Planned)**
Model Context Protocol integration enabling AI agent consumption of financial data for automated investment analysis workflows.

### Technology Stack

**Enterprise Backend Services:**
- FastAPI 0.121.1 (async endpoints, sliding window analytics)
- Flask 1.1.2 (legacy API, modular architecture)
- Apache Airflow (ETL orchestration, rate-limited API processing)
- PostgreSQL 11.13 (OLTP) → Amazon Redshift (OLAP migration planned)
- Python 3.8+ (Pydantic validation, async processing)

**Data Pipeline:**
- Financial Modeling Prep (FMP) API integration
- Rate-limited extraction (250 calls/day)
- Sliding window temporal alignment
- Enterprise error handling & retry mechanisms

**Infrastructure & Integration:**
- Docker 19.03.12 & Kubernetes v1.20.2
- Neo4j (graph database preparation)
- Model Context Protocol (AI agent integration - planned)

**Frontend Dashboard:**
- Streamlit 0.73.1 (interactive financial analytics)

**Enterprise Integration:**
- Java Spring Boot compatibility
- FINOS OpenBB Platform integration

### Getting Started

Once all the technologies are installed, clone this project's repo in your local machine.

* Backend

To spin up the Flask app and access the back-end Postgres DB, navigate to the backend folder from the project directory's root level:

$ cd backend/

Then execute:

backend $ python3 run.py 

Paste this url in a browser:

http://127.0.0.1:5000/

* Frontend

To experience the frontend dashboard, navigate to the frontend folder from the project directory's root level:

$ cd frontend/

frontend $ streamlit run src/index.py 


### Please check out a [recorded demo](https://www.youtube.com/watch?v=-OesaExIybA) of the dashboard.

