from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class PaymentCard(BaseModel):
    """Payment card information"""

    card_number: str = Field(..., description="Credit card number")
    card_holder: str = Field(..., description="Cardholder name")
    expiry_month: int = Field(..., ge=1, le=12, description="Expiry month (1-12)")
    expiry_year: int = Field(..., ge=2024, description="Expiry year")
    cvv: str = Field(..., min_length=3, max_length=4, description="Card CVV")

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        # Remove spaces and dashes
        clean_number = re.sub(r"[\s-]", "", v)
        if not clean_number.isdigit():
            raise ValueError("Card number must contain only digits")
        if len(clean_number) not in [15, 16]:
            raise ValueError("Card number must be 15 or 16 digits")
        return clean_number

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("CVV must contain only digits")
        return v


class BillingAddress(BaseModel):
    """Billing address information"""

    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"


class Customer(BaseModel):
    """Customer information"""

    customer_id: Optional[str] = None
    email: str
    phone: Optional[str] = None
    billing_address: BillingAddress


class TokenizeRequest(BaseModel):
    """Request to tokenize payment information"""

    card: PaymentCard
    customer: Customer


class TokenizeResponse(BaseModel):
    """Response with tokenized payment information"""

    token: str
    last_four_digits: str
    card_type: str
    expires_at: str
    customer_id: str
    created_at: str


class PaymentRequest(BaseModel):
    """Request to process a payment"""

    token: str
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    description: Optional[str] = None
    customer_id: str


class PaymentResponse(BaseModel):
    """Response from payment processing"""

    transaction_id: str
    status: str  # success, failed, pending
    amount: float
    currency: str
    token: str
    customer_id: str
    message: str
    processed_at: str
