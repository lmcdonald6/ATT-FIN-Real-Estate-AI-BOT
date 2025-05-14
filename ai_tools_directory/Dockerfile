FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
COPY ai_tools_directory/requirements.txt /app/service_requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r service_requirements.txt

# Copy application code
COPY src/ /app/src/
COPY ai_tools_directory/ /app/ai_tools_directory/

# Create directories for tool configurations
RUN mkdir -p /app/ai_tools_directory/configs

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/logs/ai_tools_directory \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set working directory to the service directory
WORKDIR /app/ai_tools_directory

# Default command
CMD ["python", "main.py", "list"]
