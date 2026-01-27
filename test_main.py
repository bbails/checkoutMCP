import pytest
from starlette.testclient import TestClient


# Import at module level but create test_client lazily
@pytest.fixture(scope="session")
def test_client():
    """Create test client - app is first positional arg, not keyword arg"""
    from main import app

    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_services():
    """Reset services before each test"""
    from main import tokenizer, processor

    tokenizer.tokens.clear()
    processor.transactions.clear()
    yield


class TestRootEndpoints:
    """Test root and health endpoints"""

    def test_read_root(self, test_client):
        """Test root endpoint returns API information"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Payment Mock API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestTokenization:
    """Test payment tokenization endpoint"""

    def test_tokenize_payment_success(self, test_client):
        """Test successful payment tokenization"""
        request_data = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
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
                    "country": "US",
                },
            },
        }

        response = test_client.post("/api/v1/tokenize", json=request_data)
        assert response.status_code == 201
        data = response.json()

        assert "token" in data
        assert data["token"].startswith("tok_")
        assert data["last_four_digits"] == "0366"
        assert data["card_type"] == "Visa"
        assert data["customer_id"] == "cust_123"
        assert "expires_at" in data
        assert "created_at" in data

    def test_tokenize_visa_card(self, test_client):
        """Test tokenization identifies Visa card"""
        request_data = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "test@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        response = test_client.post("/api/v1/tokenize", json=request_data)
        assert response.status_code == 201
        assert response.json()["card_type"] == "Visa"

    def test_tokenize_mastercard(self, test_client):
        """Test tokenization identifies Mastercard"""
        request_data = {
            "card": {
                "card_number": "5425233430109903",
                "card_holder": "Jane Smith",
                "expiry_month": 6,
                "expiry_year": 2026,
                "cvv": "456",
            },
            "customer": {
                "email": "jane@example.com",
                "billing_address": {
                    "street": "456 Ave",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "54321",
                    "country": "US",
                },
            },
        }

        response = test_client.post("/api/v1/tokenize", json=request_data)
        assert response.status_code == 201
        assert response.json()["card_type"] == "Mastercard"

    def test_tokenize_amex(self, test_client):
        """Test tokenization identifies American Express"""
        request_data = {
            "card": {
                "card_number": "374245455400126",
                "card_holder": "Bob Johnson",
                "expiry_month": 3,
                "expiry_year": 2027,
                "cvv": "1234",
            },
            "customer": {
                "email": "bob@example.com",
                "billing_address": {
                    "street": "789 Blvd",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "67890",
                    "country": "US",
                },
            },
        }

        response = test_client.post("/api/v1/tokenize", json=request_data)
        assert response.status_code == 201
        assert response.json()["card_type"] == "American Express"

    def test_tokenize_invalid_card_number(self, test_client):
        """Test tokenization fails with invalid card number"""
        request_data = {
            "card": {
                "card_number": "1234",
                "card_holder": "Invalid Card",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "test@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        response = test_client.post("/api/v1/tokenize", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_tokenize_generates_customer_id(self, test_client):
        """Test tokenization generates customer ID if not provided"""
        request_data = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        response = test_client.post("/api/v1/tokenize", json=request_data)
        assert response.status_code == 201
        data = response.json()
        assert "customer_id" in data
        assert data["customer_id"].startswith("cust_")


class TestPaymentProcessing:
    """Test payment processing endpoint"""

    def test_process_payment_success(self, test_client):
        """Test successful payment processing"""
        # First tokenize a card
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "customer_id": "cust_123",
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Process payment
        payment_request = {
            "token": token,
            "amount": 99.99,
            "currency": "USD",
            "customer_id": "cust_123",
            "description": "Test payment",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 201
        data = response.json()

        assert "transaction_id" in data
        assert data["transaction_id"].startswith("txn_")
        assert data["status"] in ["success", "failed", "pending"]
        assert data["amount"] == 99.99
        assert data["currency"] == "USD"
        assert data["customer_id"] == "cust_123"
        assert "message" in data
        assert "processed_at" in data

    def test_process_payment_insufficient_funds(self, test_client):
        """Test payment with insufficient funds (special amount $0.01)"""
        # Tokenize
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Process payment with special amount
        payment_request = {
            "token": token,
            "amount": 0.01,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "failed"
        assert data["message"] == "Insufficient funds"

    def test_process_payment_card_declined(self, test_client):
        """Test payment with declined card (special amount $0.02)"""
        # Tokenize
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Process payment with special amount
        payment_request = {
            "token": token,
            "amount": 0.02,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "failed"
        assert data["message"] == "Card declined"

    def test_process_payment_pending(self, test_client):
        """Test payment pending (special amount $0.03)"""
        # Tokenize
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Process payment with special amount
        payment_request = {
            "token": token,
            "amount": 0.03,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"

    def test_process_payment_large_amount(self, test_client):
        """Test payment with large amount requires review"""
        # Tokenize
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Process payment with large amount
        payment_request = {
            "token": token,
            "amount": 15000.00,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert "manual review" in data["message"].lower()

    def test_process_payment_invalid_token(self, test_client):
        """Test payment fails with invalid token"""
        payment_request = {
            "token": "tok_invalid_token",
            "amount": 99.99,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    def test_process_payment_negative_amount(self, test_client):
        """Test payment fails with negative amount"""
        payment_request = {
            "token": "tok_some_token",
            "amount": -10.00,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        response = test_client.post("/api/v1/payments", json=payment_request)
        assert response.status_code == 422  # Validation error


class TestTransactionRetrieval:
    """Test transaction retrieval endpoints"""

    def test_get_transaction_success(self, test_client):
        """Test retrieving a transaction by ID"""
        # Create a transaction first
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "customer_id": "cust_123",
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        payment_request = {
            "token": token,
            "amount": 99.99,
            "currency": "USD",
            "customer_id": "cust_123",
        }

        payment_response = test_client.post("/api/v1/payments", json=payment_request)
        transaction_id = payment_response.json()["transaction_id"]

        # Get transaction
        response = test_client.get(f"/api/v1/transactions/{transaction_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["transaction_id"] == transaction_id
        assert data["amount"] == 99.99
        assert data["customer_id"] == "cust_123"
        assert "card_info" in data

    def test_get_transaction_not_found(self, test_client):
        """Test retrieving non-existent transaction"""
        response = test_client.get("/api/v1/transactions/txn_nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_customer_transactions(self, test_client):
        """Test retrieving all transactions for a customer"""
        # Create multiple transactions
        customer_id = "cust_multi"

        for i in range(3):
            tokenize_request = {
                "card": {
                    "card_number": "4532015112830366",
                    "card_holder": "John Doe",
                    "expiry_month": 12,
                    "expiry_year": 2025,
                    "cvv": "123",
                },
                "customer": {
                    "customer_id": customer_id,
                    "email": "john@example.com",
                    "billing_address": {
                        "street": "123 St",
                        "city": "City",
                        "state": "ST",
                        "zip_code": "12345",
                        "country": "US",
                    },
                },
            }

            token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
            token = token_response.json()["token"]

            payment_request = {
                "token": token,
                "amount": 10.00 * (i + 1),
                "currency": "USD",
                "customer_id": customer_id,
            }

            test_client.post("/api/v1/payments", json=payment_request)

        # Get customer transactions
        response = test_client.get(f"/api/v1/customers/{customer_id}/transactions")
        assert response.status_code == 200
        data = response.json()

        assert data["customer_id"] == customer_id
        assert data["transaction_count"] == 3
        assert len(data["transactions"]) == 3

    def test_get_customer_transactions_empty(self, test_client):
        """Test retrieving transactions for customer with no transactions"""
        response = test_client.get("/api/v1/customers/cust_empty/transactions")
        assert response.status_code == 200
        data = response.json()

        assert data["customer_id"] == "cust_empty"
        assert data["transaction_count"] == 0
        assert len(data["transactions"]) == 0


class TestRefunds:
    """Test refund endpoint"""

    def test_refund_successful_transaction(self, test_client):
        """Test refunding a successful transaction"""
        # Create a successful transaction (using special amount to ensure success)
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "customer_id": "cust_123",
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Try to create a successful payment (may need multiple attempts due to randomness)
        transaction_id = None
        for _ in range(10):
            payment_request = {
                "token": token,
                "amount": 99.99,
                "currency": "USD",
                "customer_id": "cust_123",
            }

            payment_response = test_client.post(
                "/api/v1/payments", json=payment_request
            )
            if payment_response.json()["status"] == "success":
                transaction_id = payment_response.json()["transaction_id"]
                break

            # Re-tokenize for next attempt
            token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
            token = token_response.json()["token"]

        # Skip test if we couldn't create a successful transaction
        if transaction_id is None:
            pytest.skip("Could not create successful transaction")

        # Refund the transaction
        response = test_client.post(f"/api/v1/transactions/{transaction_id}/refund")
        assert response.status_code == 200
        data = response.json()

        assert "refund_id" in data
        assert data["original_transaction_id"] == transaction_id
        assert data["status"] == "success"

    def test_refund_nonexistent_transaction(self, test_client):
        """Test refunding non-existent transaction"""
        response = test_client.post("/api/v1/transactions/txn_nonexistent/refund")
        assert response.status_code == 404


class TestTokenInfo:
    """Test token information endpoint"""

    def test_get_token_info(self, test_client):
        """Test retrieving token information"""
        # Create a token
        tokenize_request = {
            "card": {
                "card_number": "4532015112830366",
                "card_holder": "John Doe",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
            },
            "customer": {
                "email": "john@example.com",
                "billing_address": {
                    "street": "123 St",
                    "city": "City",
                    "state": "ST",
                    "zip_code": "12345",
                    "country": "US",
                },
            },
        }

        token_response = test_client.post("/api/v1/tokenize", json=tokenize_request)
        token = token_response.json()["token"]

        # Get token info
        response = test_client.get(f"/api/v1/tokens/{token}")
        assert response.status_code == 200
        data = response.json()

        assert data["token"] == token
        assert data["last_four_digits"] == "0366"
        assert data["card_type"] == "Visa"
        assert data["is_valid"] == True
        assert "expires_at" in data
        assert "created_at" in data

        # Ensure sensitive info is not exposed
        assert "card_number_hash" not in data
        assert "card_holder" not in data

    def test_get_token_info_not_found(self, test_client):
        """Test retrieving info for non-existent token"""
        response = test_client.get("/api/v1/tokens/tok_nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
