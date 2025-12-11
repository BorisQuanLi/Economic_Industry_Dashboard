# Use an official Python runtime as a parent image (specifically a slim version for smaller size)
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install the necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Uvicorn
ENV PORT=8000

# Command to run the application using uvicorn when the container starts
# The command runs the 'app' object inside 'main.py' file using the host 0.0.0.0
# The --reload flag is omitted for production-style deployment
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
