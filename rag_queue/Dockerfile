FROM python:3.11-slim

WORKDIR /app

# Install only the bare minimum system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Use a cache mount to speed up subsequent builds
RUN pip install --no-cache-dir -r requirements.txt

COPY . .