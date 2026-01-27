import random
import secrets
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class PaymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class PaymentProcessor:
    """Service to handle payment processing"""

    def __init__(self):
        # In-memory storage for transactions
        self.transactions: Dict[str, dict] = {}

    def process_payment(
        self,
        token: str,
        amount: float,
        currency: str,
        customer_id: str,
        description: Optional[str] = None,
        token_data: Optional[dict] = None,
    ) -> dict:
        """
        Process a payment using a tokenized card
        Simulates payment processing with mock results
        """
        # Generate transaction ID
        transaction_id = self._generate_transaction_id()

        # Simulate payment processing (90% success rate)
        status, message = self._simulate_processing(amount)

        # Create transaction record
        transaction = {
            "transaction_id": transaction_id,
            "token": token,
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id,
            "description": description,
            "status": status,
            "message": message,
            "processed_at": datetime.utcnow().isoformat(),
            "card_info": {
                "last_four": (
                    token_data.get("last_four_digits") if token_data else "XXXX"
                ),
                "card_type": token_data.get("card_type") if token_data else "Unknown",
            },
        }

        # Store transaction
        self.transactions[transaction_id] = transaction

        return transaction

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(8)
        return f"txn_{timestamp}_{random_part}"

    def _simulate_processing(self, amount: float) -> tuple:
        """
        Simulate payment processing outcome
        Returns (status, message) tuple
        """
        # Special amounts for testing specific scenarios
        if amount == 0.01:
            return PaymentStatus.FAILED, "Insufficient funds"
        elif amount == 0.02:
            return PaymentStatus.FAILED, "Card declined"
        elif amount == 0.03:
            return PaymentStatus.PENDING, "Payment pending verification"
        elif amount >= 10000:
            return PaymentStatus.PENDING, "Large transaction - manual review required"

        # Random simulation (90% success rate)
        outcome = random.random()

        if outcome < 0.90:
            return PaymentStatus.SUCCESS, "Payment processed successfully"
        elif outcome < 0.95:
            return PaymentStatus.FAILED, "Card declined by issuer"
        else:
            return PaymentStatus.PENDING, "Payment under review"

    def get_transaction(self, transaction_id: str) -> Optional[dict]:
        """Retrieve transaction by ID"""
        return self.transactions.get(transaction_id)

    def get_customer_transactions(self, customer_id: str) -> list:
        """Get all transactions for a customer"""
        return [
            tx for tx in self.transactions.values() if tx["customer_id"] == customer_id
        ]

    def refund_transaction(self, transaction_id: str) -> Optional[dict]:
        """Simulate a refund for a transaction"""
        transaction = self.transactions.get(transaction_id)

        if not transaction:
            return None

        if transaction["status"] != PaymentStatus.SUCCESS:
            return {
                "success": False,
                "message": "Only successful transactions can be refunded",
            }

        # Create refund transaction
        refund_id = self._generate_transaction_id()
        refund = {
            "refund_id": refund_id,
            "original_transaction_id": transaction_id,
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "customer_id": transaction["customer_id"],
            "status": PaymentStatus.SUCCESS,
            "message": "Refund processed successfully",
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Store refund as a transaction
        self.transactions[refund_id] = refund

        # Mark original transaction as refunded
        transaction["refunded"] = True
        transaction["refund_id"] = refund_id

        return refund
