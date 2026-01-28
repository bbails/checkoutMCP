"""
Payment Agent - Azure AI Agents Integration

This agent uses Azure AI Agents SDK to create an AI agent that consumes
the Payment MCP API as tools.
"""

import os
import json
import httpx
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

# Load environment variables
load_dotenv()

# Configuration
MCP_API_URL = os.getenv("MCP_API_URL", "http://localhost:8001")
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME", "payment-agent")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.2-chat")


class AzurePaymentAgent:
    """AI Agent using Azure AI Agents SDK with Payment MCP API tools"""

    def __init__(self):
        # Validate required environment variables
        if not PROJECT_ENDPOINT:
            raise ValueError("PROJECT_ENDPOINT environment variable is required")

        # Initialize Azure AI Agents Client
        self.credential = DefaultAzureCredential()
        self.agents_client = AgentsClient(
            endpoint=PROJECT_ENDPOINT,
            credential=self.credential,
        )

        # Initialize HTTP client for MCP API
        self.http_client = httpx.Client()
        self.mcp_api_url = MCP_API_URL

        # Load tools from MCP API
        self.tools = self._load_mcp_tools()

        # Create agent with tools
        self.agent = self._create_agent()

        # Thread will be created per conversation
        self.current_thread_id = None

        print(f"✓ Azure Agent created: {self.agent.id}")
        print(f"✓ Loaded {len(self.tools)} tools from MCP API")

    def _load_mcp_tools(self):
        """Load tools from MCP API and convert to Azure format"""
        try:
            response = self.http_client.get(f"{self.mcp_api_url}/mcp/tools/list")
            response.raise_for_status()
            data = response.json()

            # Convert MCP tools to Azure function format
            azure_tools = []
            for tool in data["tools"]:
                azure_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["inputSchema"],
                        },
                    }
                )

            return azure_tools
        except Exception as e:
            print(f"✗ Failed to load MCP tools: {e}")
            return []

    def _create_agent(self):
        """Create Azure AI agent with MCP tools"""
        print(f"Debug: Creating agent with {len(self.tools)} tools")
        print(
            f"Debug: First tool sample: {self.tools[0] if self.tools else 'No tools'}"
        )

        agent = self.agents_client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name=AGENT_NAME,
            instructions="""You are a helpful payment processing assistant. You have access to payment tools to:
- Tokenize credit/debit cards for secure storage
- Process payments using tokenized cards
- Retrieve transaction details
- Get customer transaction history
- Process refunds
- Get token information

When users provide payment card information, always tokenize it first before processing payments.
Be helpful, accurate, and secure. Always confirm important actions before executing them.

Important: When calling tools, extract all required parameters from the user's message.""",
            tools=self.tools,
        )

        print(f"Debug: Agent created with ID: {agent.id}")
        print(f"Debug: Agent tools: {getattr(agent, 'tools', 'No tools attribute')}")

        return agent

    def _execute_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool via MCP API"""
        try:
            response = self.http_client.post(
                f"{self.mcp_api_url}/mcp/tools/call",
                json={"name": tool_name, "arguments": arguments},
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from content
            if "content" in data and len(data["content"]) > 0:
                return data["content"][0]["text"]
            return json.dumps(data)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def chat(self, message: str) -> str:
        """Send a message and get response from the agent"""
        try:
            # Create thread and process run with message
            print(f"Debug: Creating thread and run...")
            run = self.agents_client.create_thread_and_process_run(
                agent_id=self.agent.id,
                thread={"messages": [{"role": "user", "content": message}]},
            )

            # Save thread ID for this conversation
            self.current_thread_id = run.thread_id

            # Debug: Print run details
            print(f"Debug: Run ID: {run.id}")
            print(f"Debug: Run status: {run.status}")
            print(f"Debug: Run model: {getattr(run, 'model', 'No model')}")
            print(f"Debug: Run agent_id: {run.agent_id}")

            # Check if there are any errors
            if hasattr(run, "last_error") and run.last_error:
                print(f"Debug: Run error: {run.last_error}")

            if hasattr(run, "incomplete_details") and run.incomplete_details:
                print(f"Debug: Incomplete details: {run.incomplete_details}")

            # Check usage/token info
            if hasattr(run, "usage") and run.usage:
                print(f"Debug: Run usage: {run.usage}")

            # Print ALL run attributes to see what we're missing
            all_attrs = {k: v for k, v in run.items() if not k.startswith("_")}
            print(f"Debug: All run data: {str(all_attrs)[:500]}")

            # Get messages from the thread after run completes
            if run.status == "completed":
                # Use REST API to get messages
                from azure.core.rest import HttpRequest
                import time

                # Get API version from SDK config
                api_version = getattr(
                    self.agents_client._config, "api_version", "2024-12-01-preview"
                )

                # Build the correct URL for messages endpoint with api-version
                base_url = self.agents_client._config.endpoint.rstrip("/")
                messages_url = f"{base_url}/threads/{run.thread_id}/messages?api-version={api_version}"

                # Wait a bit before fetching messages
                time.sleep(1)

                request = HttpRequest(method="GET", url=messages_url)

                response = self.agents_client.send_request(request)

                if response.status_code == 200:
                    messages_data = response.json()

                    print(
                        f"Debug: Found {len(messages_data.get('data', []))} total messages"
                    )

                    # Print all messages for debugging
                    for idx, msg in enumerate(messages_data.get("data", [])):
                        print(
                            f"Debug: Message {idx}: role={msg.get('role')}, content_count={len(msg.get('content', []))}"
                        )

                    # Find the most recent assistant message
                    if "data" in messages_data and messages_data["data"]:
                        for msg in messages_data["data"]:
                            if msg.get("role") == "assistant":
                                # Extract text content
                                for content in msg.get("content", []):
                                    if content.get("type") == "text":
                                        text_value = content.get("text", {}).get(
                                            "value", ""
                                        )
                                        if text_value:
                                            return text_value

                return "No response from assistant"

            return f"Run status: {run.status}"

        except Exception as e:
            import traceback

            print(f"Debug: Exception traceback:\n{traceback.format_exc()}")
            return f"Error: {str(e)}"

    def reset_thread(self):
        """Reset conversation (next chat will create new thread)"""
        self.current_thread_id = None
        print("✓ Conversation reset")


def main():
    """Interactive Azure agent demo"""
    print("\n" + "=" * 60)
    print("  Azure Payment Agent - AI Assistant with MCP Tools")
    print("=" * 60)
    print("\nThis agent uses Azure AI Agents SDK to consume MCP API")
    print("\nCapabilities:")
    print("  • Tokenize payment cards")
    print("  • Process payments")
    print("  • View transactions")
    print("  • Process refunds")
    print("  • Get token information")
    print("\nCommands:")
    print("  'exit' or 'quit' - End conversation")
    print("  'reset' - Start new conversation")
    print("  'help' - Show example prompts")
    print("=" * 60 + "\n")

    # Check required environment variables
    if not os.getenv("PROJECT_ENDPOINT"):
        print("⚠️  Required environment variables:")
        print("   PROJECT_ENDPOINT - Your Azure AI Project endpoint")
        print(
            "   MODEL_DEPLOYMENT_NAME - Your model deployment name (default: gpt-5.2-chat)"
        )
        print("   AGENT_NAME - Agent name (optional, default: payment-agent)")
        print("\nExample:")
        print(
            '   export PROJECT_ENDPOINT="https://your-project.cognitiveservices.azure.com"'
        )
        print('   export MODEL_DEPLOYMENT_NAME="gpt-5.2-chat"')
        return

    try:
        # Initialize agent
        agent = AzurePaymentAgent()

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
                    agent.reset_thread()
                    continue

                if user_input.lower() == "help":
                    print("\n💡 Example prompts:")
                    print(
                        "  • Tokenize card 4532015112830366, John Doe, exp 12/2025, cvv 123"
                    )
                    print("  • Process a $50 payment for customer cust_123")
                    print("  • Show transactions for customer cust_123")
                    print("  • Refund transaction txn_abc123")
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

    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {e}\n")


if __name__ == "__main__":
    main()
