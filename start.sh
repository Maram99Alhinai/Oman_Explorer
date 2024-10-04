#!/bin/bash

# Start cloud_sql_proxy in background
cloud_sql_proxy --port 3307 sohail-437105:europe-west3:sohail-ocv1 &

# Configure ngrok
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Start ngrok in background
ngrok http 8000 --domain=adapting-moccasin-vastly.ngrok-free.app &

# Wait for a few seconds to ensure services are up
sleep 5

# Start the Flask application
python main.py