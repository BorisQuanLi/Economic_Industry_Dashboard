# Economic Industry Dashboard

## Installation

```bash
# Create and activate virtual environment
python3 -m venv sp500-dashboard-venv
source sp500-dashboard-venv/bin/activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

## Setup

1. Create virtual environment:
```bash
python3 -m venv sp500-dashboard-venv
source sp500-dashboard-venv/bin/activate
```

2. Sync dependencies:
```bash
python3 scripts/package_manager.py --sync
```

3. Start services:
```bash
# Backend API
python3 -m backend.api.src

# Frontend Dashboard
streamlit run frontend/dashboard/app.py
```

## Development

```bash
# Run tests with coverage
python3 -m pytest backend/tests/

# Install new dependencies
python3 -m pip install <package-name>
```

### Managing Dependencies

- Add new packages to root `requirements.txt`
- Run `python3 scripts/package_manager.py --sync` to update component requirements
- The sync script maintains consistent versions across all requirements files

## Problem Description

This Project makes API calls to ingest the most recent 8 quarters of financial statements filed by the S&P 500 publicly listed companies, then stores the data on a Postgres DB, utilizing the Adapter and Model-View-Controller (MVC) design patterns along the way.

A Flask API app allows the user to query aggregate and company-level data such as average quarterly revenue, cost, and price/earnings ratios, returning the results in JSON format in a web browser.

Various plots based on these data can be viewed in an interactive dashboard in a browser, where a user can select different economic sectors and sub-sectors, companies, and financial performance indicators — for example, a cross-sector comparison of average quarterly earnings over the last 8 quarters.

## Design Patterns & Architecture

This project demonstrates several enterprise-grade design patterns and architectural choices:

### Design Patterns
- **Adapter Pattern**: Standardizes diverse financial data sources into a consistent format
- **ORM (Object-Relational Mapping)**: Manages database operations through SQLAlchemy
- **MVC (Model-View-Controller)**: Separates concerns in both backend and frontend
- **Object-Process Methodology (OPM)**:
  - Objects: Financial statements, Companies, Sectors, User queries
  - Processes: Data ingestion, Transformation, Analysis
  - States: Raw data, Processed data, Analyzed results

### Architecture Patterns
- **ETL Pipeline**: Extract (API) → Transform (Adapters) → Load (PostgreSQL)
- **Event-Driven**: Real-time data updates trigger dashboard refreshes
- **Microservices**: Separate services for data ingestion, processing, and visualization
- **Domain-Driven Design**: Financial domain concepts guide the codebase structure

### Containerization & Cloud Deployment
- Complete Dockerization of all components
- Multi-container orchestration with Kubernetes
- AWS service integration:
  - Compute: EC2/ECS
  - Database: RDS PostgreSQL
  - Data Warehouse: Redshift
  - Storage: S3
  - Container Orchestration: EKS

## Architecture
- Data Lake: AWS S3
- Data Warehouse: AWS Redshift
- Orchestration: Apache Airflow
- Transformations: dbt
- Visualization: Streamlit (leveraging Python for custom interactive dashboards)

## Technologies

Backend:

- PostgreSQL 11.13
- Flask 1.1.2
- Python 3.8
- Pandas 1.1.4
- Docker 19.03.12
- Kubernetes v1.20.2
- pytest (for testing)

Frontend:

- Streamlit 0.73.1 (a Python library)

Build and Development Tools:

- Make 4.x
- pip (Python package manager)
- venv (Python virtual environment)
- git (Version control)

### Cloud Infrastructure
- AWS (S3, Redshift, EKS)
- Terraform
- Apache Airflow
- dbt
- Streamlit (Python-based visualization)

## Getting Started

Once all the technologies are installed, clone this project's repo in your local machine.

### Backend Setup

1. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv sp500-dashboard-venv

# Activate virtual environment
source sp500-dashboard-venv/bin/activate  # On Unix/macOS
# or
.\sp500-dashboard-venv\Scripts\activate  # On Windows
```

2. Install all dependencies (may take 5-10 minutes):
```bash
python3 -m pip install -r requirements.txt  # Single command to install all packages
```

3. Navigate to the backend folder:
```bash
cd backend/
```

4. Initialize the database (for development environment):
```bash
python3 manage.py init_db --env dev  # 'dev' selects development configuration
```

5. Build initial data (optional: specify a sector):
```bash
python3 manage.py build_data  # Build all sectors
python3 manage.py build_data --sector "Technology"  # Build specific sector
```

6. Run the Flask application:
```bash
python3 manage.py run --env dev
```

The API will be available at: http://127.0.0.1:5000/

### Frontend Setup

To experience the frontend dashboard, navigate to the frontend folder from the project directory's root level:

$ cd frontend/

frontend $ streamlit run src/index.py 

## Build System

This project uses Make as its build system. Make is a platform-agnostic build automation tool that comes pre-installed on most Unix-like systems (Linux, macOS). For Windows users, Make is available through:
- Windows Subsystem for Linux (WSL)
- MinGW
- Cygwin

> Note: Make is not written in Python - it's a standalone tool written in C.

### Quick Start with Make Commands

For first-time setup, run these commands in order:
```bash
make setup-venv            # Step 1: Set up Python virtual environment
make install-requirements  # Step 2: Install all required packages
```

#### For Data Professionals & Developers
```bash
make test                # Run all tests
make setup              # Initialize cloud infrastructure
make deploy            # Deploy to Kubernetes
make clean             # Tear down infrastructure
make clean-venv        # Remove virtual environment if needed
```

#### For Business Users & Analysts
After initial setup, you only need these commands:
```bash
source sp500-dashboard-venv/bin/activate  # Step 1: Activate the environment
cd frontend                               # Step 2: Go to frontend directory
python3 -m streamlit run src/index.py     # Step 3: Launch the dashboard
```

The dashboard will open automatically in your default web browser.

## Development Roadmap
### Stage 1: Core Implementation
- Cloud infrastructure setup
- Data pipeline development
- Warehouse optimization
- Dashboard migration

### Stage 2: Advanced Features (Future)
- CI/CD pipeline
- Automated testing
- Infrastructure as Code
- Monitoring and alerting

### Please check out a [recorded demo](https://www.youtube.com/watch?v=-OesaExIybA) of the dashboard.

## Development Setup

Make sure you have Python 3.10+ installed. Then:

```bash
# Create and activate virtual environment
python3 -m venv sp500-dashboard-venv
source sp500-dashboard-venv/bin/activate  # On Windows use: sp500-dashboard-venv\Scripts\activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

