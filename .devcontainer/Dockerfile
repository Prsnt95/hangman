# Base image
FROM python:3.12-slim

WORKDIR /workspace

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install PostgreSQL client and git
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*
RUN node --version && npm --version

# Expose FastAPI port
EXPOSE 8000 3000

# Default command (can override in compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
