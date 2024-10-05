FROM python:3.11.4-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cloud_sql_proxy and ngrok
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/local/bin/cloud_sql_proxy \
    && chmod +x /usr/local/bin/cloud_sql_proxy \
    && wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz \
    && tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin \
    && rm ngrok-v3-stable-linux-amd64.tgz

# Create necessary directories
RUN mkdir -p /app/data /app/credentials

# Copy application code
COPY . .

# Make the start script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]