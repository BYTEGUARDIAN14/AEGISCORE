FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for git operations, trivy, and builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Semgrep
RUN pip install --no-cache-dir semgrep

# Install Bandit
RUN pip install --no-cache-dir bandit

# Download and install Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Copy application code
COPY . .

# Create directories for ML models and temp repos
RUN mkdir -p /app/models /tmp/repos

# Expose API port
EXPOSE 8000

# Default command — can be overridden in docker-compose
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
