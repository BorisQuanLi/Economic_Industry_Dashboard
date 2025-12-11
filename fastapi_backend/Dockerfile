# Use an official Python runtime as a parent image (specifically a slim version for smaller size)
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY fastapi_backend/requirements.txt ./

# Install the necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the fastapi_backend application code
COPY fastapi_backend/ ./

# Copy the etl_service package (needed for DB models and queries)
COPY etl_service/ ./etl_service/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Uvicorn
ENV PORT=8000
ENV PYTHONPATH=/app

# Command to run the application using uvicorn when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
