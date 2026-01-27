#!/usr/bin/env python3
"""
Payment MCP Server - Stdio Implementation

This is a proper MCP server that communicates via stdin/stdout
and can be configured in VS Code, GitHub Copilot, or Claude Desktop.
"""

import json
import sys
import os
from typing import Any, Dict, List
from mcp_server import PaymentMCPServer

# Initialize payment server
payment_server = PaymentMCPServer()


def send_response(response: Dict[str, Any]):
    """Send a JSON-RPC response to stdout."""
    json_str = json.dumps(response)
    sys.stdout.write(json_str + "\n")
    sys.stdout.flush()


def send_error(request_id: Any, code: int, message: str):
    """Send an error response."""
    send_response(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
    )


def handle_initialize(request_id: Any):
    """Handle the initialize request."""
    send_response(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "0.1.0",
                "serverInfo": {"name": "payment-mcp-server", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        }
    )


def handle_list_tools(request_id: Any):
    """Handle tools/list request."""
    tools = payment_server.get_tools()

    # Convert to MCP tool format
    mcp_tools = []
    for tool in tools:
        func = tool["function"]
        mcp_tools.append(
            {
                "name": func["name"],
                "description": func["description"],
                "inputSchema": func["parameters"],
            }
        )

    send_response({"jsonrpc": "2.0", "id": request_id, "result": {"tools": mcp_tools}})


def handle_call_tool(request_id: Any, params: Dict[str, Any]):
    """Handle tools/call request."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        send_error(request_id, -32602, "Missing tool name")
        return

    try:
        # Execute the tool
        result = payment_server.execute_tool(tool_name, arguments)

        send_response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": result}]},
            }
        )
    except Exception as e:
        send_error(request_id, -32603, f"Tool execution failed: {str(e)}")


def handle_request(request: Dict[str, Any]):
    """Handle incoming JSON-RPC request."""
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        handle_initialize(request_id)
    elif method == "tools/list":
        handle_list_tools(request_id)
    elif method == "tools/call":
        handle_call_tool(request_id, params)
    else:
        send_error(request_id, -32601, f"Method not found: {method}")


def main():
    """Main server loop - reads from stdin, writes to stdout."""
    # Log to stderr for debugging
    sys.stderr.write("Payment MCP Server starting...\n")
    sys.stderr.flush()

    try:
        # Read requests from stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                handle_request(request)
            except json.JSONDecodeError as e:
                sys.stderr.write(f"Invalid JSON: {str(e)}\n")
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"Error handling request: {str(e)}\n")
                sys.stderr.flush()

    except KeyboardInterrupt:
        sys.stderr.write("Server stopped by user\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"Fatal error: {str(e)}\n")
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
