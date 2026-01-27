#!/usr/bin/env python3
"""
Interactive Demo for Payment MCP Server

This script demonstrates how to use the Payment MCP Server
in an interactive conversational mode.
"""

import json
from mcp_server import get_payment_tools, execute_payment_function


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("  Payment MCP Server - Interactive Demo")
    print("=" * 70)
    print("\nThis MCP server provides payment processing capabilities that can be")
    print("used by AI agents, chatbots, and automated workflows.\n")


def show_menu():
    """Show available operations menu."""
    print("\n" + "-" * 70)
    print("Available Operations:")
    print("-" * 70)
    print("1. Tokenize a Payment Card")
    print("2. Process a Payment")
    print("3. Get Transaction Details")
    print("4. Get Customer Transactions")
    print("5. Refund a Transaction")
    print("6. Get Token Information")
    print("7. Show All Available Tools")
    print("8. Run Quick Demo")
    print("9. Exit")
    print("-" * 70)


def tokenize_card_interactive():
    """Interactive card tokenization."""
    print("\n📝 Tokenize Payment Card")
    print("-" * 70)

    print("\nUsing test card: Visa 4532015112830366")

    args = {
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
        "billing_country": "US",
    }

    print("\nExecuting: tokenize_payment_card")
    result = execute_payment_function("tokenize_payment_card", json.dumps(args))
    result_data = json.loads(result)

    print("\n✅ Result:")
    print(json.dumps(result_data, indent=2))

    return result_data.get("token")


def process_payment_interactive(token=None):
    """Interactive payment processing."""
    print("\n💳 Process Payment")
    print("-" * 70)

    if not token:
        print("\nNo token provided. Please tokenize a card first.")
        return

    print(f"\nUsing token: {token}")
    print("Amount: $99.99")

    args = {
        "token": token,
        "amount": 99.99,
        "currency": "USD",
        "customer_id": "cust_demo",
        "description": "Interactive demo payment",
    }

    print("\nExecuting: process_payment")
    result = execute_payment_function("process_payment", json.dumps(args))
    result_data = json.loads(result)

    print("\n✅ Result:")
    print(json.dumps(result_data, indent=2))

    return result_data.get("transaction_id")


def get_transaction_interactive(transaction_id=None):
    """Interactive transaction retrieval."""
    print("\n🔍 Get Transaction Details")
    print("-" * 70)

    if not transaction_id:
        transaction_id = input("\nEnter transaction ID: ").strip()

    if not transaction_id:
        print("No transaction ID provided.")
        return

    args = {"transaction_id": transaction_id}

    print(f"\nExecuting: get_transaction for {transaction_id}")
    result = execute_payment_function("get_transaction", json.dumps(args))
    result_data = json.loads(result)

    print("\n✅ Result:")
    print(json.dumps(result_data, indent=2))


def show_tools():
    """Display all available tools."""
    print("\n🔧 Available Payment Tools")
    print("=" * 70)

    tools = get_payment_tools()
    for i, tool in enumerate(tools, 1):
        func = tool["function"]
        print(f"\n{i}. {func['name']}")
        print(f"   Description: {func['description']}")
        print(
            f"   Parameters: {len(func['parameters'].get('properties', {}))} required fields"
        )


def run_quick_demo():
    """Run a complete demonstration."""
    print("\n🚀 Running Quick Demo")
    print("=" * 70)

    # Step 1: Tokenize
    print("\n[Step 1/3] Tokenizing card...")
    token = tokenize_card_interactive()

    input("\nPress Enter to continue...")

    # Step 2: Process payment
    print("\n[Step 2/3] Processing payment...")
    transaction_id = process_payment_interactive(token)

    input("\nPress Enter to continue...")

    # Step 3: Get transaction
    print("\n[Step 3/3] Retrieving transaction details...")
    get_transaction_interactive(transaction_id)

    print("\n✅ Demo completed!")


def main():
    """Main interactive loop."""
    print_banner()

    print("⚠️  Make sure the Payment API is running on http://localhost:8000")
    input("\nPress Enter to continue...")

    current_token = None
    current_transaction = None

    while True:
        show_menu()

        try:
            choice = input("\nSelect an option (1-9): ").strip()

            if choice == "1":
                current_token = tokenize_card_interactive()

            elif choice == "2":
                if not current_token:
                    print("\n⚠️  No token available. Tokenizing a card first...")
                    current_token = tokenize_card_interactive()
                current_transaction = process_payment_interactive(current_token)

            elif choice == "3":
                get_transaction_interactive(current_transaction)

            elif choice == "4":
                customer_id = input(
                    "\nEnter customer ID (or press Enter for 'cust_demo'): "
                ).strip()
                if not customer_id:
                    customer_id = "cust_demo"
                args = {"customer_id": customer_id}
                result = execute_payment_function(
                    "get_customer_transactions", json.dumps(args)
                )
                print("\n✅ Result:")
                print(json.dumps(json.loads(result), indent=2))

            elif choice == "5":
                if not current_transaction:
                    current_transaction = input(
                        "\nEnter transaction ID to refund: "
                    ).strip()
                if current_transaction:
                    args = {"transaction_id": current_transaction}
                    result = execute_payment_function(
                        "refund_transaction", json.dumps(args)
                    )
                    print("\n✅ Result:")
                    print(json.dumps(json.loads(result), indent=2))

            elif choice == "6":
                if not current_token:
                    current_token = input("\nEnter token: ").strip()
                if current_token:
                    args = {"token": current_token}
                    result = execute_payment_function(
                        "get_token_info", json.dumps(args)
                    )
                    print("\n✅ Result:")
                    print(json.dumps(json.loads(result), indent=2))

            elif choice == "7":
                show_tools()

            elif choice == "8":
                run_quick_demo()

            elif choice == "9":
                print("\n👋 Goodbye!")
                break

            else:
                print("\n⚠️  Invalid option. Please select 1-9.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
