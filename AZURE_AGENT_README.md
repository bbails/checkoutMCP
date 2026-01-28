# Azure Payment Agent - Quick Start

## Azure AI Framework Integration

This agent uses **Azure AI Projects SDK** to create an intelligent agent that consumes the Payment MCP API as tools.

## Architecture

```
User → Azure Payment Agent → MCP API Server → Payment API
          (Azure AI)          (Port 8001)     (Port 8000)
```

## Prerequisites

### 1. Azure Setup

You need an Azure AI Project. Create one at: https://ai.azure.com

Once created, get your:
- **Project Endpoint**: `https://your-project.cognitiveservices.azure.com`
- **Model Deployment**: Deploy a model (e.g., `gpt-4`, `gpt-4-turbo`)

### 2. Authentication

The agent uses `DefaultAzureCredential`, which tries multiple authentication methods:
- Azure CLI: `az login`
- Environment variables
- Managed identity (when deployed to Azure)

**Easiest for local development:**
```bash
az login
```

### 3. Local Services Running

```bash
# Terminal 1: Payment API
python main.py

# Terminal 2: MCP API Server
python mcp_api_server.py
```

## Installation

```bash
# Install Azure packages
pip install azure-identity azure-ai-projects python-dotenv

# Or install all requirements
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your Azure details:

```env
PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com
MODEL_DEPLOYMENT_NAME=gpt-4
AGENT_NAME=payment-agent
MCP_API_URL=http://localhost:8001
```

## Usage

### Interactive Mode

```bash
python azure_payment_agent.py
```

Example conversation:
```
🧑 You: Tokenize card 4532015112830366, John Doe, exp 12/2025, cvv 123, 
email john@test.com, billing 123 Main St, NY, NY, 10001

🔧 Executing: tokenize_payment_card

🤖 Agent: I've successfully tokenized the card. The token is tok_abc123...
and it will expire in 24 hours. Would you like to process a payment with it?

🧑 You: Yes, charge customer cust_123 for $99.99

🔧 Executing: process_payment

🤖 Agent: Payment processed successfully! Transaction ID: txn_xyz789
Amount: $99.99 USD, Status: completed
```

### Programmatic Usage

```python
from azure_payment_agent import AzurePaymentAgent

# Initialize
agent = AzurePaymentAgent()

# Chat
response = agent.chat(
    "Tokenize card 4532015112830366, John Doe, exp 12/2025"
)
print(response)

# Multi-turn conversation (agent maintains context)
agent.chat("Now process a $50 payment for customer cust_456")
agent.chat("Show me the transaction history")

# Reset conversation
agent.reset_thread()
```

### Run Examples

```bash
python azure_agent_examples.py
```

## Features

✅ **Azure AI Integration** - Uses Azure AI Projects SDK
✅ **Function Calling** - Automatic tool selection and execution
✅ **MCP Protocol** - Consumes MCP API as tool backend
✅ **Stateful Conversations** - Uses Azure threads for context
✅ **Secure Authentication** - DefaultAzureCredential for Azure auth
✅ **Natural Language** - Understands complex payment requests

## Available Tools

The agent automatically loads these tools from MCP API:

1. `tokenize_payment_card` - Tokenize credit/debit cards
2. `process_payment` - Process payments with tokens
3. `get_transaction` - Get transaction details
4. `get_customer_transactions` - View customer transaction history
5. `refund_transaction` - Process refunds
6. `get_token_info` - Check token validity

## Azure AI Project Setup

### Step-by-Step

1. **Go to Azure AI Studio**: https://ai.azure.com
2. **Create a Project**:
   - Click "New project"
   - Choose your subscription and resource group
   - Select region
3. **Deploy a Model**:
   - Go to "Deployments"
   - Click "Deploy model"
   - Select `gpt-4` or `gpt-4-turbo`
   - Note the deployment name
4. **Get Project Endpoint**:
   - Go to project settings
   - Copy the endpoint URL

### Example Project Endpoint Format

```
https://eastus.api.azureml.ms/projects/your-project-id
```

or

```
https://your-project.cognitiveservices.azure.com
```

## Authentication Methods

### Azure CLI (Recommended for local dev)
```bash
az login
```

### Service Principal
```bash
export AZURE_CLIENT_ID="..."
export AZURE_CLIENT_SECRET="..."
export AZURE_TENANT_ID="..."
```

### Managed Identity
Automatically works when deployed to Azure services (App Service, Functions, etc.)

## Troubleshooting

### "PROJECT_ENDPOINT environment variable is required"
- Make sure `.env` file exists with correct values
- Or export variables: `export PROJECT_ENDPOINT="..."`

### "DefaultAzureCredential failed to authenticate"
- Run `az login` to authenticate via Azure CLI
- Verify you have access to the Azure subscription

### "Model deployment not found"
- Check MODEL_DEPLOYMENT_NAME matches your deployment in Azure AI Studio
- Verify the deployment is active and running

### "Connection refused" errors
- Ensure Payment API is running on port 8000
- Ensure MCP API Server is running on port 8001

### Agent not executing tools
- Check MCP API Server logs for errors
- Verify tools are loaded: agent should print "Loaded X tools from MCP API"

## Cost Considerations

- **Azure AI Models**: Charges based on tokens (input + output)
- **MCP API**: Free (local HTTP server)
- **Payment API**: Free (mock service)

Monitor usage in Azure Portal → Cost Management

## Deployment to Azure

### Deploy as Azure Function

```bash
# Create function app
func init PaymentAgentFunc --python
cd PaymentAgentFunc

# Copy agent code
cp ../azure_payment_agent.py .

# Create function
func new --name ProcessPayment --template "HTTP trigger"

# Deploy
func azure functionapp publish <your-function-app-name>
```

### Deploy as Azure App Service

```bash
# Create web app
az webapp up --name payment-agent-app \
  --resource-group your-rg \
  --runtime PYTHON:3.11

# Configure environment variables
az webapp config appsettings set \
  --name payment-agent-app \
  --settings PROJECT_ENDPOINT="..." \
             MODEL_DEPLOYMENT_NAME="gpt-4"
```

## Comparison: Azure vs OpenAI

| Feature | Azure Agent | OpenAI Agent |
|---------|------------|--------------|
| SDK | azure-ai-projects | openai |
| Auth | Azure credentials | API key |
| Models | Azure deployments | OpenAI models |
| Cost | Azure pricing | OpenAI pricing |
| Compliance | Azure compliance | OpenAI compliance |
| Data residency | Configurable | OpenAI servers |

**Choose Azure if:**
- You have Azure subscription
- Need data residency control
- Want Azure enterprise features
- Require Azure compliance

**Choose OpenAI if:**
- Simpler setup (just API key)
- Don't need Azure features
- Want latest OpenAI models immediately

## Next Steps

1. ✅ Set up Azure AI Project
2. ✅ Configure `.env` file
3. ✅ Run `az login`
4. ✅ Start Payment API and MCP API Server
5. ✅ Run `python azure_payment_agent.py`

## Resources

- [Azure AI Studio](https://ai.azure.com)
- [Azure AI Projects SDK Docs](https://learn.microsoft.com/azure/ai-studio/)
- [Payment API README](README.md)
- [MCP Configuration](MCP_CONFIGURATION.md)

## License

MIT License - See main README.md
