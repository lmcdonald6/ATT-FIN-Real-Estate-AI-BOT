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
COPY api_gateway_service/requirements.txt /app/service_requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r service_requirements.txt

# Copy application code
COPY src/ /app/src/
COPY api_gateway_service/ /app/api_gateway_service/

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/logs/api_gateway_service \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set working directory to the service directory
WORKDIR /app/api_gateway_service

# Expose the API Gateway port
EXPOSE 8080

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
