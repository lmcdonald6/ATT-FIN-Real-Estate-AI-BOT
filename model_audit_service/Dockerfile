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
COPY model_audit_service/requirements.txt /app/service_requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r service_requirements.txt

# Copy application code
COPY src/ /app/src/
COPY model_audit_service/ /app/model_audit_service/

# Create directories for audit results and reports
RUN mkdir -p /app/model_audit_service/audit_results \
    && mkdir -p /app/model_audit_service/reports

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/logs/model_audit_service \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set working directory to the service directory
WORKDIR /app/model_audit_service

# Default command
CMD ["python", "main.py"]
