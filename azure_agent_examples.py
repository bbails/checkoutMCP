"""
Azure Payment Agent - Example Usage

Demonstrates how to use the Azure AI agent with MCP tools.
"""

import os
from dotenv import load_dotenv
from azure_payment_agent import AzurePaymentAgent

load_dotenv()


def check_prerequisites():
    """Check if all required environment variables are set"""
    required = {
        "PROJECT_ENDPOINT": "Azure AI Project endpoint URL",
        "MCP_API_URL": "MCP API Server URL (default: http://localhost:8001)",
    }

    missing = []
    for key, description in required.items():
        if key == "MCP_API_URL":
            if not os.getenv(key):
                print(f"⚠️  {key} not set, using default: http://localhost:8001")
        elif not os.getenv(key):
            missing.append(f"  {key} - {description}")

    if missing:
        print("❌ Missing required environment variables:\n")
        print("\n".join(missing))
        print("\nSet them in .env file or export them:")
        print(
            'export PROJECT_ENDPOINT="https://your-project.cognitiveservices.azure.com"'
        )
        return False

    return True


def example_tokenize_and_pay():
    """Example: Tokenize card and process payment"""
    print("\n" + "=" * 60)
    print("Example: Tokenize Card and Process Payment")
    print("=" * 60)

    if not check_prerequisites():
        return

    try:
        agent = AzurePaymentAgent()

        # Step 1: Tokenize
        print("\n📝 Step 1: Tokenizing card...")
        response1 = agent.chat(
            "Tokenize this card: 4532015112830366, cardholder John Doe, "
            "expires 12/2025, cvv 123, email john@example.com, "
            "billing address 123 Main St, New York, NY, 10001"
        )
        print(f"Response: {response1}")

        # Step 2: Process payment
        print("\n💳 Step 2: Processing payment...")
        response2 = agent.chat(
            "Now process a payment of $99.99 for customer cust_john_123 "
            "with description 'Product purchase'"
        )
        print(f"Response: {response2}")

        # Step 3: View transactions
        print("\n📊 Step 3: Viewing transactions...")
        response3 = agent.chat("Show me all transactions for customer cust_john_123")
        print(f"Response: {response3}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_natural_conversation():
    """Example: Natural conversation with the agent"""
    print("\n" + "=" * 60)
    print("Example: Natural Conversation Flow")
    print("=" * 60)

    if not check_prerequisites():
        return

    try:
        agent = AzurePaymentAgent()

        conversation = [
            "Hi, I need help processing a payment",
            "The customer's card number is 5555555555554444",
            "Cardholder name is Jane Smith, expires 06/2026, cvv 456",
            "Email is jane@test.com, billing address is 789 Oak Ave, Austin, TX, 73301",
            "Great! Now charge $150.00 to customer cust_jane_789 for 'Service subscription'",
        ]

        for i, message in enumerate(conversation, 1):
            print(f"\n🧑 User ({i}/{len(conversation)}): {message}")
            response = agent.chat(message)
            print(f"🤖 Agent: {response}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_error_scenarios():
    """Example: Testing error handling"""
    print("\n" + "=" * 60)
    print("Example: Error Handling Scenarios")
    print("=" * 60)

    if not check_prerequisites():
        return

    try:
        agent = AzurePaymentAgent()

        # Tokenize first
        print("\n📝 Tokenizing test card...")
        agent.chat(
            "Tokenize card 378282246310005, Alice Test, exp 12/2025, cvv 1234, "
            "email alice@test.com, billing 111 Test St, Test City, TC, 00000"
        )

        # Test insufficient funds
        print("\n💳 Testing insufficient funds scenario ($0.01)...")
        response = agent.chat("Process payment of $0.01 for customer cust_test_error")
        print(f"Response: {response}")

        # Test declined
        print("\n💳 Testing declined scenario ($0.02)...")
        agent.chat(
            "Tokenize a new card: 4111111111111111, Test User, exp 03/2027, cvv 999, email test@test.com, billing 222 Test St, Test, TS, 11111"
        )
        response = agent.chat(
            "Process payment of $0.02 for customer cust_test_declined"
        )
        print(f"Response: {response}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("  Azure Payment Agent - Example Usage")
    print("=" * 60)
    print("\n⚠️  Prerequisites:")
    print("  1. Payment API running on port 8000")
    print("  2. MCP API Server running on port 8001")
    print("  3. Azure AI Project configured with environment variables")
    print("\nStarting examples...\n")

    try:
        # Example 1
        example_tokenize_and_pay()
        input("\nPress Enter to continue to next example...")

        # Example 2
        example_natural_conversation()
        input("\nPress Enter to continue to next example...")

        # Example 3
        example_error_scenarios()

        print("\n" + "=" * 60)
        print("  All Examples Completed!")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted\n")


if __name__ == "__main__":
    main()
