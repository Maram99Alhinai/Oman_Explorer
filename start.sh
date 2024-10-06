#!/bin/bash
set -e

# Function to wait for a service to become available
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=$4
    local attempt=1
    
    echo "Waiting for $service to be ready..."
    while ! nc -z $host $port; do
        if [ $attempt -ge $max_attempts ]; then
            echo "$service failed to become ready after $max_attempts attempts"
            return 1
        fi
        echo "Attempt $attempt: $service not ready yet..."
        sleep 2
        ((attempt++))
    done
    echo "$service is ready!"
}

# Start Cloud SQL Proxy in the background
echo "Starting Cloud SQL Proxy..."
cloud_sql_proxy --instances="sohail-437105:europe-west3:sohail-ocv1=tcp:0.0.0.0:3307" &
CLOUD_SQL_PID=$!

# Wait for Cloud SQL Proxy to be ready
wait_for_service localhost 3307 "Cloud SQL Proxy" 30 || exit 1

# Configure and start ngrok
echo "Configuring ngrok..."
if [ -n "$NGROK_AUTHTOKEN" ]; then
    ngrok config add-authtoken "$NGROK_AUTHTOKEN"
    ngrok http 8080 --domain=adapting-moccasin-vastly.ngrok-free.app &
    NGROK_PID=$!
else
    echo "Warning: NGROK_AUTHTOKEN not set. Skipping ngrok setup."
fi

# Wait a moment for services to initialize
sleep 2

# Start Gunicorn application server
echo "Starting Gunicorn..."
gunicorn --workers 4 --worker-class gevent --bind 0.0.0.0:8080 main:app &
GUNICORN_PID=$!

# Trap SIGTERM and SIGINT
trap 'kill $CLOUD_SQL_PID $NGROK_PID $GUNICORN_PID 2>/dev/null' SIGTERM SIGINT

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?