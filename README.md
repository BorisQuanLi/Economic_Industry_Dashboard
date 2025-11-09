
### Description

**Enterprise Financial Data Pipeline** - A three-stage modernization showcasing Wall Street-grade data engineering:

🏗️ **STAGE 1 COMPLETE**: Flask Backend Refactoring with Blueprint Architecture  
🚀 **STAGE 2 COMPLETE**: Airflow ETL Automation with Sliding Window Algorithm  
🎯 **STAGE 3 IN PROGRESS**: FastAPI High-Performance API Layer  

This project demonstrates enterprise-grade automation solving real investment banking challenges, including Apple's disparate Q4 filing dates vs industry peers. The system processes S&P 500 financial statements with rate-limited API integration, stores data in PostgreSQL, and provides both Flask and FastAPI endpoints for financial analytics.

**Key Innovation**: Sliding window algorithm enabling accurate cross-sector analysis despite disparate corporate filing schedules.

Various plots based on these data can be viewed in an interactive dashboard in a browser, where a user can select different economic sectors and sub-sectors, companies, and financial performance indicators — for example, a cross-sector comparison of average quarterly earnings over the last 8 quarters.

### Technology Stack

**Backend (Multi-Framework Architecture):**
- Flask 1.1.2 (Blueprint-based modular architecture)
- FastAPI (High-performance async endpoints) - *IN DEVELOPMENT*
- Apache Airflow (ETL orchestration with sliding window algorithm)
- PostgreSQL 11.13 (OLTP) → Amazon Redshift (OLAP)
- Python 3.8+ with Pandas 1.1.4
- Docker 19.03.12 & Kubernetes v1.20.2

**Data Pipeline:**
- Financial Modeling Prep (FMP) API integration
- Rate-limited extraction (250 calls/day)
- Sliding window temporal alignment
- Enterprise error handling & retry mechanisms

**Frontend:**
- Streamlit 0.73.1 (Interactive dashboard)

**Enterprise Integration:**
- Neo4j graph database preparation
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

