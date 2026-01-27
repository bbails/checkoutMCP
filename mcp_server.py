"""
Payment MCP Server using Microsoft Agent Framework

An MCP-compatible server that provides payment processing tools using
Microsoft Agent Framework for function calling.
"""

import json
import os
from typing import Any, Dict, List, Optional
import httpx

# Payment API configuration
PAYMENT_API_URL = os.getenv("PAYMENT_API_URL", "http://localhost:8000")


class PaymentMCPServer:
    """MCP Server for Payment API using Microsoft Agent Framework."""

    def __init__(self, api_url: str = PAYMENT_API_URL):
        self.api_url = api_url
        self.client = httpx.Client(timeout=30.0)

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get payment processing tools in OpenAI function format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "tokenize_payment_card",
                    "description": "Tokenize a payment card for secure storage and future transactions. Returns a token that expires in 24 hours.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "card_number": {
                                "type": "string",
                                "description": "Credit card number (15-16 digits)",
                            },
                            "card_holder": {
                                "type": "string",
                                "description": "Cardholder name",
                            },
                            "expiry_month": {
                                "type": "integer",
                                "description": "Expiry month (1-12)",
                            },
                            "expiry_year": {
                                "type": "integer",
                                "description": "Expiry year (e.g., 2025)",
                            },
                            "cvv": {
                                "type": "string",
                                "description": "Card CVV (3-4 digits)",
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "Optional customer ID",
                            },
                            "customer_email": {
                                "type": "string",
                                "description": "Customer email address",
                            },
                            "billing_street": {
                                "type": "string",
                                "description": "Billing street address",
                            },
                            "billing_city": {
                                "type": "string",
                                "description": "Billing city",
                            },
                            "billing_state": {
                                "type": "string",
                                "description": "Billing state",
                            },
                            "billing_zip": {
                                "type": "string",
                                "description": "Billing ZIP code",
                            },
                            "billing_country": {
                                "type": "string",
                                "description": "Billing country (default: US)",
                            },
                        },
                        "required": [
                            "card_number",
                            "card_holder",
                            "expiry_month",
                            "expiry_year",
                            "cvv",
                            "customer_email",
                            "billing_street",
                            "billing_city",
                            "billing_state",
                            "billing_zip",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "process_payment",
                    "description": "Process a payment using a tokenized card. Special test amounts: $0.01 (insufficient funds), $0.02 (card declined), $0.03 (pending), $10,000+ (manual review).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "token": {
                                "type": "string",
                                "description": "Payment token from tokenization",
                            },
                            "amount": {
                                "type": "number",
                                "description": "Payment amount (must be positive)",
                            },
                            "currency": {
                                "type": "string",
                                "description": "Currency code (default: USD)",
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "Customer identifier",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional payment description",
                            },
                        },
                        "required": ["token", "amount", "customer_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_transaction",
                    "description": "Retrieve details of a specific transaction by its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "transaction_id": {
                                "type": "string",
                                "description": "Transaction ID to retrieve",
                            },
                        },
                        "required": ["transaction_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer_transactions",
                    "description": "Get all transactions for a specific customer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "Customer ID to query transactions for",
                            },
                        },
                        "required": ["customer_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "refund_transaction",
                    "description": "Process a refund for a successful transaction. Only successful transactions can be refunded.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "transaction_id": {
                                "type": "string",
                                "description": "Transaction ID to refund",
                            },
                        },
                        "required": ["transaction_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_token_info",
                    "description": "Get information about a payment token, including its validity and expiration.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "token": {
                                "type": "string",
                                "description": "Payment token to query",
                            },
                        },
                        "required": ["token"],
                    },
                },
            },
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a payment tool and return the result."""
        try:
            if tool_name == "tokenize_payment_card":
                return self._tokenize_card(arguments)
            elif tool_name == "process_payment":
                return self._process_payment(arguments)
            elif tool_name == "get_transaction":
                return self._get_transaction(arguments)
            elif tool_name == "get_customer_transactions":
                return self._get_customer_transactions(arguments)
            elif tool_name == "refund_transaction":
                return self._refund_transaction(arguments)
            elif tool_name == "get_token_info":
                return self._get_token_info(arguments)
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _tokenize_card(self, args: Dict[str, Any]) -> str:
        """Tokenize a payment card."""
        request_data = {
            "card": {
                "card_number": args["card_number"],
                "card_holder": args["card_holder"],
                "expiry_month": args["expiry_month"],
                "expiry_year": args["expiry_year"],
                "cvv": args["cvv"],
            },
            "customer": {
                "customer_id": args.get("customer_id"),
                "email": args["customer_email"],
                "billing_address": {
                    "street": args["billing_street"],
                    "city": args["billing_city"],
                    "state": args["billing_state"],
                    "zip_code": args["billing_zip"],
                    "country": args.get("billing_country", "US"),
                },
            },
        }

        response = self.client.post(
            f"{self.api_url}/api/v1/tokenize",
            json=request_data,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def _process_payment(self, args: Dict[str, Any]) -> str:
        """Process a payment."""
        request_data = {
            "token": args["token"],
            "amount": args["amount"],
            "currency": args.get("currency", "USD"),
            "customer_id": args["customer_id"],
            "description": args.get("description"),
        }

        response = self.client.post(
            f"{self.api_url}/api/v1/payments",
            json=request_data,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def _get_transaction(self, args: Dict[str, Any]) -> str:
        """Get transaction details."""
        transaction_id = args["transaction_id"]
        response = self.client.get(
            f"{self.api_url}/api/v1/transactions/{transaction_id}"
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def _get_customer_transactions(self, args: Dict[str, Any]) -> str:
        """Get all transactions for a customer."""
        customer_id = args["customer_id"]
        response = self.client.get(
            f"{self.api_url}/api/v1/customers/{customer_id}/transactions"
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def _refund_transaction(self, args: Dict[str, Any]) -> str:
        """Refund a transaction."""
        transaction_id = args["transaction_id"]
        response = self.client.post(
            f"{self.api_url}/api/v1/transactions/{transaction_id}/refund"
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def _get_token_info(self, args: Dict[str, Any]) -> str:
        """Get token information."""
        token = args["token"]
        response = self.client.get(f"{self.api_url}/api/v1/tokens/{token}")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Global server instance
payment_server = PaymentMCPServer()


def get_payment_tools():
    """Get payment tools for use with OpenAI function calling."""
    return payment_server.get_tools()


def execute_payment_function(function_name: str, function_args: str) -> str:
    """Execute a payment function with given arguments."""
    try:
        args = (
            json.loads(function_args)
            if isinstance(function_args, str)
            else function_args
        )
        return payment_server.execute_tool(function_name, args)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON arguments: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    # Example usage
    print("Payment MCP Server using Microsoft Agent Framework")
    print("=" * 60)
    print("\nAvailable Tools:")
    tools = get_payment_tools()
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   {tool['function']['description']}")

    print("\n" + "=" * 60)
    print("Use get_payment_tools() to get tool definitions")
    print("Use execute_payment_function(name, args) to execute tools")
    print("=" * 60)
