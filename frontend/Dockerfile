# Use a modern, secure, and smaller Python base image
FROM python:3.11-slim-bookworm

# Set the working directory
WORKDIR /usr/src/app

# Create a non-root user for security
RUN useradd -m -s /bin/bash appuser
USER appuser

# Upgrade pip and install wheel
RUN python -m pip install --upgrade pip wheel

# Copy only the requirements file to leverage Docker cache
COPY --chown=appuser:appuser ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser ./.env ./.env
COPY --chown=appuser:appuser ./__init__.py ./__init__.py

# Add the user's local bin directory to the PATH
# This ensures that executables installed by pip (like streamlit) are found
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Expose the port the app runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "src/index.py"]
