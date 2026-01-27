# Payment MCP Server

This directory contains an MCP (Model Context Protocol) server that wraps the Payment Mock API, allowing AI assistants and other MCP clients to interact with the payment system.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI assistants like Claude to use external tools and data sources. This MCP server exposes the Payment API functionality as a set of tools that can be called by AI assistants.

## Available MCP Tools

The Payment MCP server provides these tools:

1. **tokenize_payment_card** - Tokenize a payment card for secure storage
2. **process_payment** - Process a payment using a token
3. **get_transaction** - Get transaction details by ID
4. **get_customer_transactions** - Get all transactions for a customer
5. **refund_transaction** - Refund a successful transaction
6. **get_token_info** - Get information about a payment token

## Setup

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Update Requirements

The MCP SDK has been added to `requirements.txt`. Install it:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure MCP in Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "payment": {
      "command": "python",
      "args": [
        "/{PATHTOPROJECT}/mcp_server.py"
      ],
      "env": {
        "PAYMENT_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Note**: Update the path to match your installation directory.

### 4. Activate Virtual Environment in Config (Alternative)

If you want to use the virtual environment, modify the config:

```json
{
  "mcpServers": {
    "payment": {
      "command": "{PATHTOPROJECT}/.venv/bin/python",
      "args": [
        "/{PATHTOPROJECT}/mcp_server.py"
      ],
      "env": {
        "PAYMENT_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Usage

### 1. Start the Payment API Server

First, make sure the Payment API is running:

```bash
cd /{PATHTOPROJECT}
source .venv/bin/activate
python main.py
```

The API should be running on http://localhost:8000

### 2. Test the MCP Server

Test the MCP server directly:

```bash
# Run the MCP server (it uses stdio protocol)
python mcp_server.py
```

### 3. Use with Claude Desktop

Once configured in Claude Desktop:

1. Restart Claude Desktop
2. The payment tools will be available automatically
3. You can ask Claude to perform payment operations:

**Example prompts:**

- "Tokenize this credit card: 4532015112830366, John Doe, expires 12/2025, CVV 123, email john@example.com, address 123 Main St, New York, NY 10001"
- "Process a payment of $50 using token tok_abc123 for customer cust_123"
- "Get transaction details for txn_20260127_abc123"
- "Show all transactions for customer cust_123"
- "Refund transaction txn_20260127_abc123"

## MCP Tool Examples

### Tokenize Card

```json
{
  "tool": "tokenize_payment_card",
  "arguments": {
    "card_number": "4532015112830366",
    "card_holder": "John Doe",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123",
    "customer_email": "john@example.com",
    "billing_street": "123 Main St",
    "billing_city": "New York",
    "billing_state": "NY",
    "billing_zip": "10001",
    "billing_country": "US"
  }
}
```

### Process Payment

```json
{
  "tool": "process_payment",
  "arguments": {
    "token": "tok_abc123...",
    "amount": 99.99,
    "currency": "USD",
    "customer_id": "cust_123",
    "description": "Order #12345"
  }
}
```

## Testing Special Scenarios

The MCP server supports all the same test scenarios as the API:

- **$0.01** → Insufficient funds
- **$0.02** → Card declined  
- **$0.03** → Payment pending
- **$10,000+** → Manual review required

## Troubleshooting

### MCP Server Not Appearing in Claude

1. Check that the path in `claude_desktop_config.json` is correct
2. Restart Claude Desktop completely
3. Check Claude Desktop logs for errors

### Connection Errors

1. Ensure the Payment API is running on http://localhost:8000
2. Test the API directly: `curl http://localhost:8000/health`
3. Check firewall settings

### Import Errors

Make sure the MCP SDK is installed:
```bash
pip install mcp
```

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
│   (MCP Client)  │
└────────┬────────┘
         │ MCP Protocol (stdio)
         │
┌────────▼────────┐
│   mcp_server.py │
│  (MCP Server)   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│    main.py      │
│  (Payment API)  │
└─────────────────┘
```

## Files

- `mcp_server.py` - MCP server implementation
- `mcp_config.json` - Example MCP configuration
- `MCP_README.md` - This documentation
- `main.py` - Payment API server
- `test_mcp.py` - MCP server tests (optional)

## Next Steps

1. Install the MCP SDK: `pip install mcp`
2. Configure Claude Desktop with the MCP server
3. Start the Payment API server
4. Restart Claude Desktop
5. Try asking Claude to process payments!
