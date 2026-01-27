# Payment Mock API

A mock HTTP API service that simulates a payment system with card tokenization and payment processing capabilities. Built with FastAPI and Python.

## Features

- 🔐 **Payment Card Tokenization**: Securely tokenize credit card information
- 💳 **Payment Processing**: Process payments using tokenized cards
- 🔍 **Transaction Management**: Track and query payment transactions
- 💰 **Refund Support**: Process refunds for successful transactions
- 📊 **Customer Analytics**: View transaction history by customer
- 🛡️ **Card Validation**: Validates card numbers, CVV, and expiry dates
- 📝 **Automatic API Documentation**: Interactive API docs with Swagger UI

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone or navigate to the project directory:
```bash
cd PaymentMCP
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

Start the API server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Tokenize Payment Card

**POST** `/api/v1/tokenize`

Tokenize customer payment card information for secure storage.

**Request Body:**
```json
{
  "card": {
    "card_number": "4532015112830366",
    "card_holder": "John Doe",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123"
  },
  "customer": {
    "customer_id": "cust_123",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "billing_address": {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "country": "US"
    }
  }
}
```

**Response:**
```json
{
  "token": "tok_abc123def456...",
  "last_four_digits": "0366",
  "card_type": "Visa",
  "expires_at": "2026-01-28T12:00:00",
  "customer_id": "cust_123",
  "created_at": "2026-01-27T12:00:00"
}
```

### 2. Process Payment

**POST** `/api/v1/payments`

Process a payment using a previously generated token.

**Request Body:**
```json
{
  "token": "tok_abc123def456...",
  "amount": 99.99,
  "currency": "USD",
  "customer_id": "cust_123",
  "description": "Order #12345"
}
```

**Response:**
```json
{
  "transaction_id": "txn_20260127120000_a1b2c3d4",
  "status": "success",
  "amount": 99.99,
  "currency": "USD",
  "token": "tok_abc123def456...",
  "customer_id": "cust_123",
  "message": "Payment processed successfully",
  "processed_at": "2026-01-27T12:00:00"
}
```

### 3. Get Transaction

**GET** `/api/v1/transactions/{transaction_id}`

Retrieve details of a specific transaction.

**Response:**
```json
{
  "transaction_id": "txn_20260127120000_a1b2c3d4",
  "status": "success",
  "amount": 99.99,
  "currency": "USD",
  "customer_id": "cust_123",
  "description": "Order #12345",
  "processed_at": "2026-01-27T12:00:00",
  "card_info": {
    "last_four": "0366",
    "card_type": "Visa"
  }
}
```

### 4. Get Customer Transactions

**GET** `/api/v1/customers/{customer_id}/transactions`

Get all transactions for a specific customer.

### 5. Refund Transaction

**POST** `/api/v1/transactions/{transaction_id}/refund`

Process a refund for a successful transaction.

### 6. Get Token Info

**GET** `/api/v1/tokens/{token}`

Get information about a token (debugging).

## Test Card Numbers

Use these card numbers for testing different card types:

- **Visa**: 4532015112830366
- **Mastercard**: 5425233430109903
- **American Express**: 374245455400126
- **Discover**: 6011111111111117

All test cards accept any future expiry date and any 3-4 digit CVV.

## Special Test Amounts

Use these amounts to simulate specific payment scenarios:

- **$0.01** - Insufficient funds (fails)
- **$0.02** - Card declined (fails)
- **$0.03** - Payment pending verification
- **$10,000+** - Large transaction requiring manual review (pending)
- **Other amounts** - 90% success rate with random outcomes

## Card Types Supported

The API automatically detects:
- Visa (starts with 4)
- Mastercard (starts with 51-55)
- American Express (starts with 34 or 37)
- Discover (starts with 6011 or 65)

## Token Expiration

Tokens expire 24 hours after creation. Expired tokens cannot be used for payment processing.

## Error Handling

The API returns standard HTTP status codes:

- **200/201** - Success
- **400** - Bad Request (validation errors)
- **401** - Unauthorized (invalid/expired token)
- **404** - Not Found (transaction/token not found)
- **500** - Internal Server Error

Error response format:
```json
{
  "detail": "Error message description"
}
```

## Data Storage

**Note**: This is a mock service. All data is stored in-memory and will be lost when the server restarts. In a production environment, you would use:
- Secure database for token storage
- PCI-DSS compliant infrastructure
- Proper encryption for sensitive data
- Payment gateway integration

## Architecture

```
├── main.py                 # FastAPI application and endpoints
├── models.py               # Pydantic models for request/response
├── tokenizer.py            # Card tokenization service
├── payment_processor.py    # Payment processing logic
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Security Notes

⚠️ **This is a mock service for development/testing only**

In a real payment system:
- Never store raw card numbers
- Use PCI-DSS compliant infrastructure
- Implement proper authentication and authorization
- Use HTTPS for all communications
- Integrate with actual payment gateways (Stripe, PayPal, etc.)
- Implement proper audit logging
- Use secure key management systems

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (create test file first)
pytest
```

### Making Changes

The server runs in development mode with auto-reload. Changes to Python files will automatically restart the server.

## License

MIT License

## Support

For issues or questions about this mock API, please refer to the API documentation at `/docs` endpoint.
