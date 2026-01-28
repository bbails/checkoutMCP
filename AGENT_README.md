# Payment Agent - AI Assistant with MCP Tools

An AI-powered conversational agent that uses the Payment MCP API as its tool backend. The agent can understand natural language requests and execute payment operations intelligently.

## Architecture

```
User Request → Payment Agent (OpenAI GPT-4) → MCP API Server → Payment API
                    ↓                              ↓               ↓
              Function Calling              Tool Execution    Actual Processing
```

## Features

- 🤖 **Natural Language Interface**: Talk to the agent in plain English
- 🔧 **Automatic Tool Selection**: Agent chooses the right tools based on context
- 💳 **Smart Payment Processing**: Automatically tokenizes cards before payments
- 📊 **Transaction Management**: View history, process refunds, check status
- 🔄 **Multi-turn Conversations**: Context-aware across multiple messages
- ⚡ **Real-time Execution**: Tools execute via MCP API in real-time

## Available Capabilities

The agent has access to these payment tools:

1. **Tokenize Payment Cards** - Securely tokenize credit/debit cards
2. **Process Payments** - Charge tokenized payment methods
3. **Get Transaction Details** - Retrieve specific transaction information
4. **Get Customer Transactions** - View all transactions for a customer
5. **Process Refunds** - Refund completed transactions
6. **Get Token Information** - Check token validity and details

## Prerequisites

1. **Payment API** running on port 8000:
   ```bash
   python main.py
   ```

2. **MCP API Server** running on port 8001:
   ```bash
   python mcp_api_server.py
   ```

3. **OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   ```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='sk-...'
```

## Usage

### Interactive Mode

Run the agent in interactive chat mode:

```bash
python payment_agent.py
```

Example conversation:
```
🧑 You: I need to charge customer cust_123 for $99.99

🤖 Agent: I'll help you process that payment. To charge $99.99 to customer 
cust_123, I'll need the payment card information. Could you provide:
- Card number
- Cardholder name
- Expiry date (MM/YYYY)
- CVV
- Billing address

🧑 You: Card is 4532015112830366, John Doe, exp 12/2025, cvv 123, 
billing 123 Main St, NY, NY 10001, email john@test.com

🔧 Executing: tokenize_payment_card
🔧 Executing: process_payment

🤖 Agent: Payment successfully processed! Here are the details:
- Transaction ID: txn_abc123...
- Amount: $99.99 USD
- Status: completed
- Token used: tok_xyz...
```

### Programmatic Usage

Use the agent in your Python code:

```python
from payment_agent import PaymentAgent

# Initialize agent
agent = PaymentAgent()

# Single request
response = agent.chat(
    "Tokenize card 4532015112830366, John Doe, exp 12/2025, cvv 123"
)
print(response)

# Multi-turn conversation
agent.chat("I want to process a payment")
agent.chat("Card number is 5555555555554444")
agent.chat("Customer ID is cust_456, charge $50")

# Reset conversation
agent.reset_conversation()
```

### Run Example Scenarios

See the agent in action with pre-built examples:

```bash
python example_agent_usage.py
```

Examples include:
- Card tokenization
- Payment processing workflow
- Transaction history retrieval
- Natural conversation flow
- Error handling scenarios

## Example Prompts

Try these natural language prompts:

```
• "Tokenize this card: 4532015112830366, John Doe, exp 12/2025, cvv 123"

• "Process a $50 payment for customer cust_123"

• "Show me all transactions for customer cust_456"

• "Refund transaction txn_abc123"

• "What's the status of token tok_xyz?"

• "I need to charge someone $100. Their card is 4111111111111111..."

• "Can you tell me the transaction history for customer cust_789?"
```

## Commands

While chatting with the agent:

- `exit` or `quit` - End the conversation
- `reset` - Start a new conversation (clears history)
- `help` - Show example prompts

## Configuration

Configure via environment variables:

```bash
# Required
export OPENAI_API_KEY='sk-...'

# Optional
export MCP_API_URL='http://localhost:8001'  # Default: http://localhost:8001
```

## How It Works

1. **User Input**: You provide a natural language request
2. **Intent Understanding**: OpenAI GPT-4 interprets your intent
3. **Tool Selection**: Agent chooses appropriate payment tools
4. **Execution**: Tools execute via MCP API Server
5. **Response**: Agent formulates a natural language response

The agent uses OpenAI's function calling feature to automatically:
- Determine which tools to use
- Extract required parameters from conversation
- Execute multiple tools in sequence
- Maintain conversation context

## API Models Used

- **Model**: GPT-4 Turbo Preview
- **Features**: Function calling, multi-turn conversations
- **Temperature**: Default (balanced creativity/accuracy)

## Error Handling

The agent handles errors gracefully:

- Missing parameters: Asks for clarification
- Invalid data: Explains the issue
- API failures: Reports errors clearly
- Special test amounts: Processes correctly ($0.01 = insufficient funds, $0.02 = declined)

## Testing

All three services must be running:

```bash
# Terminal 1: Payment API
python main.py

# Terminal 2: MCP API Server
python mcp_api_server.py

# Terminal 3: Agent
python payment_agent.py
```

## Limitations

- Requires active internet connection (OpenAI API)
- OpenAI API usage incurs costs
- In-memory storage (data lost on restart)
- Mock payment processing (not production-ready)

## Extending the Agent

To add custom behavior:

```python
class CustomPaymentAgent(PaymentAgent):
    def chat(self, user_message: str) -> str:
        # Add custom pre-processing
        if "urgent" in user_message.lower():
            user_message += " (PRIORITY: HIGH)"
        
        # Call parent
        return super().chat(user_message)
```

## Troubleshooting

**Agent not responding:**
- Check OPENAI_API_KEY is set correctly
- Verify internet connection

**Tool execution fails:**
- Ensure MCP API Server is running (port 8001)
- Ensure Payment API is running (port 8000)

**"Tool not found" errors:**
- Restart MCP API Server
- Agent will reload tools on initialization

## License

MIT License - See main README.md

## Related

- [Payment API Documentation](README.md)
- [MCP Server Configuration](MCP_CONFIGURATION.md)
- [MCP Protocol Details](MCP_README.md)
