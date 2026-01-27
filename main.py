from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import uvicorn
from typing import Optional

from models import TokenizeRequest, TokenizeResponse, PaymentRequest, PaymentResponse
from tokenizer import PaymentTokenizer
from payment_processor import PaymentProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Payment Mock API",
    description="Mock Payment API with tokenization and payment processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
tokenizer = PaymentTokenizer()
processor = PaymentProcessor()


@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "service": "Payment Mock API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "tokenize": "/api/v1/tokenize",
            "process_payment": "/api/v1/payments",
            "get_transaction": "/api/v1/transactions/{transaction_id}",
            "refund": "/api/v1/transactions/{transaction_id}/refund",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(
    "/api/v1/tokenize",
    response_model=TokenizeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def tokenize_payment(request: TokenizeRequest):
    """
    Tokenize payment card information

    This endpoint accepts customer payment information and returns a secure token
    that can be used for payment processing without exposing card details.

    - **card**: Credit card information (number, holder, expiry, CVV)
    - **customer**: Customer information (email, billing address, etc.)

    Returns a token that expires in 24 hours.
    """
    try:
        # Generate customer ID if not provided
        customer_id = (
            request.customer.customer_id or f"cust_{datetime.now(timezone.utc).timestamp()}"
        )

        # Tokenize the card
        token_info = tokenizer.tokenize_card(
            card_number=request.card.card_number,
            card_holder=request.card.card_holder,
            expiry_month=request.card.expiry_month,
            expiry_year=request.card.expiry_year,
            cvv=request.card.cvv,
        )

        # Prepare response
        response = TokenizeResponse(
            token=token_info["token"],
            last_four_digits=token_info["last_four_digits"],
            card_type=token_info["card_type"],
            expires_at=token_info["expires_at"],
            customer_id=customer_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tokenization failed: {str(e)}",
        )


@app.post(
    "/api/v1/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_payment(request: PaymentRequest):
    """
    Process a payment using a tokenized card

    This endpoint processes a payment using a previously generated token.

    - **token**: Payment token from tokenization endpoint
    - **amount**: Payment amount (must be greater than 0)
    - **currency**: Currency code (default: USD)
    - **customer_id**: Customer identifier
    - **description**: Optional payment description

    Special test amounts for different scenarios:
    - $0.01 - Insufficient funds
    - $0.02 - Card declined
    - $0.03 - Payment pending
    - $10,000+ - Manual review required
    """
    try:
        # Validate token
        token_data = tokenizer.validate_token(request.token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Process payment
        transaction = processor.process_payment(
            token=request.token,
            amount=request.amount,
            currency=request.currency,
            customer_id=request.customer_id,
            description=request.description,
            token_data=token_data,
        )

        # Prepare response
        response = PaymentResponse(
            transaction_id=transaction["transaction_id"],
            status=transaction["status"],
            amount=transaction["amount"],
            currency=transaction["currency"],
            token=request.token,
            customer_id=transaction["customer_id"],
            message=transaction["message"],
            processed_at=transaction["processed_at"],
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing failed: {str(e)}",
        )


@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """
    Retrieve transaction details by transaction ID
    """
    transaction = processor.get_transaction(transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    return transaction


@app.get("/api/v1/customers/{customer_id}/transactions")
async def get_customer_transactions(customer_id: str):
    """
    Get all transactions for a specific customer
    """
    transactions = processor.get_customer_transactions(customer_id)

    return {
        "customer_id": customer_id,
        "transaction_count": len(transactions),
        "transactions": transactions,
    }


@app.post("/api/v1/transactions/{transaction_id}/refund")
async def refund_transaction(transaction_id: str):
    """
    Refund a successful transaction
    """
    refund = processor.refund_transaction(transaction_id)

    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    if not refund.get("success", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=refund.get("message", "Refund failed"),
        )

    return refund


@app.get("/api/v1/tokens/{token}")
async def get_token_info(token: str):
    """
    Get information about a token (for debugging purposes)
    """
    token_info = tokenizer.get_token_info(token)

    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    # Remove sensitive information
    safe_info = {
        "token": token_info["token"],
        "last_four_digits": token_info["last_four_digits"],
        "card_type": token_info["card_type"],
        "expires_at": token_info["expires_at"],
        "created_at": token_info["created_at"],
        "is_valid": token_info["is_valid"],
    }

    return safe_info


if __name__ == "__main__":
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
