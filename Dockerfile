FROM python:3.11.4-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ngrok
RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz \
    && tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin \
    && rm ngrok-v3-stable-linux-amd64.tgz

# Create necessary directories
RUN mkdir -p /app/data /app/credentials

# Copy application code
COPY . .

EXPOSE 8080

# The CMD instruction will be overridden by the command in docker-compose.yml
CMD ["gunicorn", "--workers", "4", "--worker-class", "gevent", "--bind", "0.0.0.0:8080", "main:app"]