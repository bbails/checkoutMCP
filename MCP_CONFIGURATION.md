# Payment MCP Server Configuration

This document explains how to configure the Payment MCP Server in various clients.

## Architecture

The Payment MCP Server runs as a **stdio-based service** that:
- Reads requests from **stdin** (standard input)
- Writes responses to **stdout** (standard output)
- Logs to **stderr** (standard error)

This allows it to be used by any MCP-compatible client.

## Configuration

### For VS Code / GitHub Copilot

Add this to your VS Code settings (`.vscode/settings.json` or User Settings):

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Use the payment MCP server for payment operations"
    }
  ],
  "mcp.servers": {
    "payment": {
      "command": "/Users/cpinzonpinto/Documents/PaymentMCP/.venv/bin/python",
      "args": [
        "/Users/cpinzonpinto/Documents/PaymentMCP/mcp_server_stdio.py"
      ],
      "env": {
        "PAYMENT_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### For Claude Desktop

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "payment": {
      "command": "/Users/cpinzonpinto/Documents/PaymentMCP/.venv/bin/python",
      "args": [
        "/Users/cpinzonpinto/Documents/PaymentMCP/mcp_server_stdio.py"
      ],
      "env": {
        "PAYMENT_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### For Microsoft Copilot Studio

Create an agent configuration file:

```json
{
  "name": "PaymentAgent",
  "tools": [
    {
      "type": "mcp",
      "server": {
        "command": "/Users/cpinzonpinto/Documents/PaymentMCP/.venv/bin/python",
        "args": ["/Users/cpinzonpinto/Documents/PaymentMCP/mcp_server_stdio.py"]
      }
    }
  ]
}
```

## Testing the MCP Server

### 1. Manual Test (Command Line)

You can test the MCP server manually by piping JSON-RPC requests:

```bash
cd /Users/cpinzonpinto/Documents/PaymentMCP
source .venv/bin/activate

# Test initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python mcp_server_stdio.py

# Test list tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python mcp_server_stdio.py
```

### 2. Automated Test Script

Run the test script:

```bash
python test_mcp_stdio.py
```

## Available Tools

The MCP server exposes these tools:

1. **tokenize_payment_card** - Tokenize credit card information
2. **process_payment** - Process a payment using a token
3. **get_transaction** - Get transaction details
4. **get_customer_transactions** - Get all customer transactions
5. **refund_transaction** - Refund a transaction
6. **get_token_info** - Get token information

## Requirements

### Prerequisites
1. **Payment API must be running** on http://localhost:8000
   ```bash
   python main.py
   ```

2. **Python virtual environment** must be activated
   ```bash
   source .venv/bin/activate
   ```

### Client Requirements
- VS Code with GitHub Copilot extension
- OR Claude Desktop application
- OR Microsoft Copilot Studio
- OR any MCP-compatible client

## Troubleshooting

### MCP Server Not Appearing in VS Code

1. Check VS Code settings are correct
2. Restart VS Code completely
3. Check the Output panel → "MCP Servers" for errors
4. Verify Python path is correct: `/Users/cpinzonpinto/Documents/PaymentMCP/.venv/bin/python`

### Connection Errors

1. Ensure Payment API is running: `curl http://localhost:8000/health`
2. Check server logs in stderr
3. Verify file permissions: `chmod +x mcp_server_stdio.py`

### Tool Execution Fails

1. Verify Payment API is accessible
2. Check request format matches expected schema
3. Review error messages in stderr output

## How It Works

```
┌─────────────────┐
│   VS Code /     │
│  Claude Desktop │
│   (MCP Client)  │
└────────┬────────┘
         │ JSON-RPC over stdio
         │
┌────────▼────────────┐
│ mcp_server_stdio.py │
│   (MCP Server)      │
└────────┬────────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   main.py       │
│ (Payment API)   │
└─────────────────┘
```

## Example Usage in VS Code

Once configured, you can ask GitHub Copilot:

- "Tokenize this credit card: 4532015112830366, John Doe, expires 12/2025, CVV 123"
- "Process a payment of $50 using the token"
- "Show me all transactions for customer cust_123"
- "Refund transaction txn_12345"

The MCP server will automatically handle the API calls and return the results.

## Security Notes

⚠️ **Important**: This is a development/testing server. In production:

1. Use HTTPS for Payment API
2. Implement authentication and authorization
3. Add rate limiting
4. Use secure token storage
5. Comply with PCI-DSS requirements
6. Never log sensitive card data

## Learn More

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [GitHub Copilot Extensions](https://docs.github.com/copilot/github-copilot-extensions)
- [VS Code MCP Integration](https://code.visualstudio.com/docs)
