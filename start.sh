#!/bin/bash

# Start the Payment API server in the background
echo "Starting Payment API server on port 8000..."
python main.py &
PAYMENT_PID=$!

# Wait for Payment API to be ready
echo "Waiting for Payment API to be ready..."
sleep 3

# Start the MCP API server in the foreground
echo "Starting MCP API server on port 8001..."
python mcp_api_server.py &
MCP_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down servers..."
    kill $PAYMENT_PID $MCP_PID
    exit 0
}

# Trap SIGTERM and SIGINT
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait
