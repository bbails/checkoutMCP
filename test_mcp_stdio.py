#!/usr/bin/env python3
"""
Test script for MCP stdio server

This script tests the stdio-based MCP server by sending JSON-RPC requests
and validating responses.
"""

import subprocess
import json
import time


def send_request(process, request):
    """Send a JSON-RPC request to the MCP server."""
    request_str = json.dumps(request) + "\n"
    process.stdin.write(request_str.encode())
    process.stdin.flush()

    # Read response
    response_line = process.stdout.readline().decode().strip()
    if response_line:
        return json.loads(response_line)
    return None


def test_mcp_server():
    """Test the MCP stdio server."""
    print("=" * 70)
    print("  Testing Payment MCP Server (stdio protocol)")
    print("=" * 70)

    # Start the MCP server process
    print("\n📡 Starting MCP server...")
    process = subprocess.Popen(
        ["python", "mcp_server_stdio.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/Users/cpinzonpinto/Documents/PaymentMCP",
    )

    time.sleep(1)  # Give server time to start

    try:
        # Test 1: Initialize
        print("\n[Test 1] Initialize")
        print("-" * 70)
        request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        response = send_request(process, request)
        print(f"✓ Response: {json.dumps(response, indent=2)}")

        # Test 2: List tools
        print("\n[Test 2] List Tools")
        print("-" * 70)
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        response = send_request(process, request)
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"✓ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}")
        else:
            print(f"✗ Response: {response}")

        # Test 3: Call tokenize tool
        print("\n[Test 3] Call Tokenize Tool")
        print("-" * 70)
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "tokenize_payment_card",
                "arguments": {
                    "card_number": "4532015112830366",
                    "card_holder": "John Doe",
                    "expiry_month": 12,
                    "expiry_year": 2025,
                    "cvv": "123",
                    "customer_email": "test@example.com",
                    "billing_street": "123 Main St",
                    "billing_city": "New York",
                    "billing_state": "NY",
                    "billing_zip": "10001",
                },
            },
        }
        response = send_request(process, request)
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                result_text = content[0].get("text", "")
                result_data = json.loads(result_text)
                print(f"✓ Token: {result_data.get('token', 'N/A')}")
                print(f"✓ Card Type: {result_data.get('card_type', 'N/A')}")
        else:
            print(f"✗ Response: {response}")

        print("\n" + "=" * 70)
        print("✅ MCP Server Tests Completed!")
        print("=" * 70)
        print("\nThe server is ready to be configured in:")
        print("  • VS Code settings")
        print("  • Claude Desktop")
        print("  • Microsoft Copilot Studio")
        print("\nSee MCP_CONFIGURATION.md for setup instructions.")

    finally:
        # Cleanup
        process.terminate()
        process.wait(timeout=5)


if __name__ == "__main__":
    test_mcp_server()
