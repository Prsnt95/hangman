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
    && rm -rf /var/lib/apt/lists/*

# Expose FastAPI port
EXPOSE 8000

# Default command (can override in compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
