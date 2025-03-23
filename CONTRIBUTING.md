# Contributing Guide

## Project Structure

The project follows a modular architecture:

- **Backend API** (`/backend/webservice`): Flask-based REST API 
- **ETL Pipeline** (`/backend/etl`): Data extraction, transformation, and loading
- **Frontend** (`/frontend`): Streamlit dashboard

## Development Workflow

1. **Setup Environment**:
   ```bash
   python -m venv sp500-dashboard-venv
   source sp500-dashboard-venv/bin/activate  # Windows: sp500-dashboard-venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Tests**:
   ```bash
   python -m pytest backend/tests/
   ```

3. **Start Backend**:
   ```bash
   python run.py  # Development mode
   ```

4. **Coding Standards**:
   - Follow PEP 8 style guidelines
   - Document modules and public functions/classes
   - Write tests for new functionality

## Architecture Patterns

The codebase uses several design patterns:

- **Service Pattern**: Business logic encapsulated in service classes
- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: Object creation (see `service_factory.py`)
- **Blueprint Pattern**: API route modularization (Flask blueprints)

## Adding New Features

1. **Add Domain Model**: Create appropriate models under `backend/etl/transform/models/`
2. **Create Service**: Implement business logic in services
3. **Add API Endpoint**: Create route handlers in appropriate blueprint
4. **Write Tests**: Add tests for new functionality
5. **Update Documentation**: Document new features or API endpoints

## Troubleshooting

- **Import Errors**: Check Python module path; use relative imports within modules
- **Database Connection Issues**: Verify connection settings in config
- **Missing Dependencies**: Run `pip install -r requirements.txt`
