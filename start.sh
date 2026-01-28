#!/bin/bash

set -e

echo "=========================================="
echo "  Starting Payment Services"
echo "=========================================="

# Start the Payment API server in the background
echo "Starting Payment API server on port 8000..."
python main.py &
PAYMENT_PID=$!

# Wait for Payment API to be ready
echo "Waiting for Payment API to be ready..."
sleep 5

# Check if Payment API started successfully
if ! kill -0 $PAYMENT_PID 2>/dev/null; then
    echo "ERROR: Payment API failed to start"
    exit 1
fi
echo "✓ Payment API started (PID: $PAYMENT_PID)"

# Start the MCP API server in the background
echo "Starting MCP API server on port 8001..."
python mcp_api_server.py &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 3

# Check if MCP API started successfully
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo "ERROR: MCP API failed to start"
    kill $PAYMENT_PID 2>/dev/null
    exit 1
fi
echo "✓ MCP API started (PID: $MCP_PID)"

echo "=========================================="
echo "  All services running!"
echo "=========================================="

# Function to handle shutdown
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $PAYMENT_PID $MCP_PID 2>/dev/null || true
    exit 0
}

# Trap SIGTERM and SIGINT
trap cleanup SIGTERM SIGINT

# Keep container running - check both processes every 5 seconds
while true; do
    if ! kill -0 $PAYMENT_PID 2>/dev/null; then
        echo "ERROR: Payment API process died"
        kill $MCP_PID 2>/dev/null || true
        exit 1
    fi
    if ! kill -0 $MCP_PID 2>/dev/null; then
        echo "ERROR: MCP API process died"
        kill $PAYMENT_PID 2>/dev/null || true
        exit 1
    fi
    sleep 5
done
