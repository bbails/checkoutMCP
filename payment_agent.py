"""
Payment Agent - AI Agent using MCP API as Tool Backend

This agent uses OpenAI's function calling to interact with the Payment MCP API.
It can understand natural language requests and execute payment operations.
"""

import os
import json
import httpx
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Configuration
MCP_API_URL = os.getenv("MCP_API_URL", "http://localhost:8001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print(
        "⚠️  Warning: OPENAI_API_KEY not set. Set it with: export OPENAI_API_KEY='your-key'"
    )


class PaymentAgent:
    """AI Agent that uses Payment MCP API as its tool backend"""

    def __init__(self, api_url: str = MCP_API_URL):
        self.api_url = api_url
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.http_client = httpx.Client()
        self.tools = []
        self.conversation_history = []

        # Load tools from MCP API
        self._load_tools()

    def _load_tools(self):
        """Load available tools from MCP API"""
        try:
            response = self.http_client.get(f"{self.api_url}/mcp/tools/list")
            response.raise_for_status()
            data = response.json()

            # Convert MCP tools to OpenAI function format
            self.tools = []
            for tool in data["tools"]:
                self.tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["inputSchema"],
                        },
                    }
                )

            print(f"✓ Loaded {len(self.tools)} tools from MCP API")
        except Exception as e:
            print(f"✗ Failed to load tools: {e}")

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool via MCP API"""
        try:
            response = self.http_client.post(
                f"{self.api_url}/mcp/tools/call",
                json={"name": tool_name, "arguments": arguments},
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from content
            if "content" in data and len(data["content"]) > 0:
                return data["content"][0]["text"]
            return json.dumps(data)
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        Handles function calling automatically.
        """
        if not self.client:
            return "❌ OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."

        # Add user message to conversation
        self.conversation_history.append({"role": "user", "content": user_message})

        # Call OpenAI with tools
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful payment processing assistant. You have access to payment tools to:
- Tokenize credit/debit cards for secure storage
- Process payments using tokenized cards
- Retrieve transaction details
- Get customer transaction history
- Process refunds
- Get token information

When users provide payment card information, always tokenize it first before processing payments.
Be helpful, accurate, and secure. Always confirm important actions before executing them.""",
                },
                *self.conversation_history,
            ],
            tools=self.tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Check if the model wants to call functions
        if assistant_message.tool_calls:
            # Add assistant message with tool calls to history
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in assistant_message.tool_calls
                    ],
                }
            )

            # Execute all tool calls
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"🔧 Executing: {function_name}")

                # Execute via MCP API
                function_response = self._execute_tool(function_name, function_args)

                # Add tool response to conversation
                self.conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response,
                    }
                )

            # Get final response from model
            final_response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful payment processing assistant. You have access to payment tools to:
- Tokenize credit/debit cards for secure storage
- Process payments using tokenized cards
- Retrieve transaction details
- Get customer transaction history
- Process refunds
- Get token information

When users provide payment card information, always tokenize it first before processing payments.
Be helpful, accurate, and secure. Always confirm important actions before executing them.""",
                    },
                    *self.conversation_history,
                ],
            )

            final_message = final_response.choices[0].message.content
            self.conversation_history.append(
                {"role": "assistant", "content": final_message}
            )

            return final_message
        else:
            # No function call, just return the response
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message.content}
            )
            return assistant_message.content

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        print("✓ Conversation reset")


def main():
    """Interactive agent demo"""
    print("\n" + "=" * 60)
    print("  Payment Agent - AI Assistant with MCP Tools")
    print("=" * 60)
    print("\nThis agent can help you with payment operations:")
    print("  • Tokenize payment cards")
    print("  • Process payments")
    print("  • View transactions")
    print("  • Process refunds")
    print("  • Get token information")
    print("\nType 'exit' or 'quit' to end the conversation")
    print("Type 'reset' to start a new conversation")
    print("Type 'help' to see example prompts")
    print("=" * 60 + "\n")

    # Initialize agent
    agent = PaymentAgent()

    if not OPENAI_API_KEY:
        print("\n⚠️  Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'\n")
        return

    # Conversation loop
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye!\n")
                break

            if user_input.lower() == "reset":
                agent.reset_conversation()
                continue

            if user_input.lower() == "help":
                print("\n💡 Example prompts:")
                print(
                    "  • Tokenize this card: 4532015112830366, John Doe, exp 12/2025, cvv 123"
                )
                print("  • Process a $50 payment for customer cust_123")
                print("  • Show me transactions for customer cust_123")
                print("  • Refund transaction txn_abc123")
                print("  • What info do you have on token tok_xyz?")
                continue

            # Get agent response
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
