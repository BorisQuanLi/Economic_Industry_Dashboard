# Economic Industry Dashboard - Build Configuration
#
# Usage:
#   make setup-venv       - Create Python virtual environment
#   make install-requirements - Install Python packages (takes ~5-10 mins)
#   make clean-venv       - Remove virtual environment
#   make test            - Run test suite
#   make deploy          - Deploy to Kubernetes cluster
#
# Note: Always activate virtual environment before running commands:
#   source sp500-dashboard-venv/bin/activate

.PHONY: setup deploy test clean setup-venv clean-venv install-requirements verify-packages install-missing

setup:
	terraform -chdir=infrastructure/terraform/aws init
	terraform -chdir=infrastructure/terraform/aws apply

deploy:
	kubectl apply -f k8s/

test:
	python -m pytest backend/tests/

clean:
	terraform -chdir=infrastructure/terraform/aws destroy

setup-venv:
	@if [ -d "sp500-dashboard-venv" ]; then \
		echo "Warning: Virtual environment already exists. Run 'make clean-venv' first."; \
		exit 1; \
	fi
	python3 -m venv sp500-dashboard-venv
	@echo "Virtual environment created. Run 'source sp500-dashboard-venv/bin/activate' to activate."

clean-venv:
	@echo "Please run 'deactivate' manually if the virtual environment is active"
	rm -rf sp500-dashboard-venv
	@echo "Virtual environment removed. Please start a new terminal session."

verify-packages:
	@echo "Verifying required packages..."
	@python3 scripts/package_manager.py

install-missing:
	@echo "Installing missing packages..."
	@python3 scripts/package_manager.py --install

install-requirements:
	@echo "Setting up pip (< 1 min)..."
	python3 -m pip install --upgrade pip

	@echo "Installing packages (this may take 5-10 minutes)..."
	@echo "Note: Large packages like streamlit and plotly will take longer"
	pip install --no-cache-dir -r requirements.txt

	@echo "Verifying installations..."
	@python3 -c "import streamlit; import plotly; import pandas; import numpy" || (echo "Core imports failed. Please check the installation logs." && exit 1)

	@echo "✓ Installation completed successfully!"
