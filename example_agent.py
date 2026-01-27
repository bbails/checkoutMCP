"""
Example: Using Payment MCP Server with OpenAI Agent

This example demonstrates how to use the Payment MCP Server with OpenAI's
function calling to process payments conversationally.
"""

import os
import json
from openai import OpenAI
from mcp_server import get_payment_tools, execute_payment_function

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get payment tools
tools = get_payment_tools()


def run_agent_conversation(user_message: str, conversation_history: list = None):
    """
    Run an agent conversation with payment tools.

    Args:
        user_message: The user's message
        conversation_history: Previous conversation messages
    """
    if conversation_history is None:
        conversation_history = []

    # Add user message
    conversation_history.append({"role": "user", "content": user_message})

    # Call OpenAI with function calling
    response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation_history,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Add assistant response to history
    conversation_history.append(response_message)

    # Handle tool calls if any
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments

            print(f"\n🔧 Calling function: {function_name}")
            print(f"Arguments: {function_args}")

            # Execute the payment function
            function_response = execute_payment_function(function_name, function_args)

            print(f"Response: {function_response}")

            # Add function response to conversation
            conversation_history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        # Get final response from the model
        second_response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation_history,
        )

        final_message = second_response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": final_message})

        return final_message, conversation_history
    else:
        return response_message.content, conversation_history


def main():
    """Run example payment conversations."""
    print("=" * 80)
    print("Payment Agent with Microsoft AI Framework")
    print("=" * 80)

    conversation = []

    # Example 1: Tokenize a card
    print("\n\n📝 Example 1: Tokenize a Visa Card")
    print("-" * 80)

    response, conversation = run_agent_conversation(
        "Tokenize this Visa card: number 4532015112830366, holder John Doe, "
        "expires 12/2025, CVV 123. Customer email is john@example.com, "
        "billing address: 123 Main St, New York, NY 10001, US",
        conversation,
    )
    print(f"\n✅ Assistant: {response}")

    # Example 2: Process a payment
    print("\n\n💳 Example 2: Process a Payment")
    print("-" * 80)

    response, conversation = run_agent_conversation(
        "Now process a payment of $99.99 for customer cust_123 using that token. "
        "Description: 'Order #12345'",
        conversation,
    )
    print(f"\n✅ Assistant: {response}")

    # Example 3: Get transaction
    print("\n\n📊 Example 3: Check Transaction Status")
    print("-" * 80)

    response, conversation = run_agent_conversation(
        "What are the details of that transaction?", conversation
    )
    print(f"\n✅ Assistant: {response}")

    # Example 4: Test insufficient funds
    print("\n\n❌ Example 4: Test Insufficient Funds")
    print("-" * 80)

    # Start new conversation
    conversation = []

    response, conversation = run_agent_conversation(
        "Tokenize this Mastercard: 5425233430109903, Jane Smith, expires 06/2026, "
        "CVV 456, email jane@example.com, address 456 Oak Ave, LA, CA 90001",
        conversation,
    )
    print(f"\n✅ Assistant: {response}")

    response, conversation = run_agent_conversation(
        "Process a payment of $0.01 for customer cust_test using that token",
        conversation,
    )
    print(f"\n✅ Assistant: {response}")

    print("\n\n" + "=" * 80)
    print("✨ Examples Complete!")
    print("=" * 80)


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key'")
    else:
        main()
