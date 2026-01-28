# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install bash (for wait -n support)
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY models.py .
COPY tokenizer.py .
COPY payment_processor.py .
COPY mcp_server.py .
COPY mcp_api_server.py .
COPY start.sh .

# Fix line endings (Windows CRLF to Unix LF) and make executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose both ports
EXPOSE 8000 8001

# Set environment variables
ENV PAYMENT_API_URL=http://localhost:8000
ENV MCP_API_URL=http://localhost:8001
ENV STG_API_URL=https://stg.checkout1.worklearngrow.online

# Run the startup script
CMD ["./start.sh"]
