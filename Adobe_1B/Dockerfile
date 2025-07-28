FROM python:3.9-slim

# Set platform for AMD64 compatibility
FROM --platform=linux/amd64 python:3.9-slimB

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script and config
COPY main.py .
COPY config.json .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set the entrypoint
ENTRYPOINT ["python", "main.py"] 