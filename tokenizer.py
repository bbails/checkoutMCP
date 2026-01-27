import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Optional


class PaymentTokenizer:
    """Service to handle payment card tokenization"""

    def __init__(self):
        # In-memory storage for tokens (in production, use a secure database)
        self.tokens: Dict[str, dict] = {}

    def tokenize_card(
        self,
        card_number: str,
        card_holder: str,
        expiry_month: int,
        expiry_year: int,
        cvv: str,
    ) -> dict:
        """
        Tokenize payment card information
        Returns a secure token and metadata
        """
        # Generate unique token
        token = self._generate_token(card_number)

        # Extract card type
        card_type = self._identify_card_type(card_number)

        # Get last 4 digits
        last_four = card_number[-4:]

        # Token expires in 24 hours
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Store token data (simulating secure storage)
        token_data = {
            "token": token,
            "card_number_hash": hashlib.sha256(card_number.encode()).hexdigest(),
            "last_four_digits": last_four,
            "card_holder": card_holder,
            "expiry_month": expiry_month,
            "expiry_year": expiry_year,
            "card_type": card_type,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "is_valid": True,
        }

        self.tokens[token] = token_data

        return {
            "token": token,
            "last_four_digits": last_four,
            "card_type": card_type,
            "expires_at": expires_at.isoformat(),
        }

    def _generate_token(self, card_number: str) -> str:
        """Generate a unique secure token"""
        # Combine card number with random data for uniqueness
        random_data = secrets.token_hex(16)
        timestamp = datetime.utcnow().isoformat()

        # Create hash-based token
        data = f"{card_number}:{random_data}:{timestamp}"
        token_hash = hashlib.sha256(data.encode()).hexdigest()

        # Format as token with prefix
        return f"tok_{token_hash[:32]}"

    def _identify_card_type(self, card_number: str) -> str:
        """Identify card type based on card number"""
        # Remove any spaces or dashes
        clean_number = re.sub(r"[\s-]", "", card_number)

        # Card type patterns
        if re.match(r"^4", clean_number):
            return "Visa"
        elif re.match(r"^5[1-5]", clean_number):
            return "Mastercard"
        elif re.match(r"^3[47]", clean_number):
            return "American Express"
        elif re.match(r"^6(?:011|5)", clean_number):
            return "Discover"
        else:
            return "Unknown"

    def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate if token exists and is not expired
        Returns token data if valid, None otherwise
        """
        if token not in self.tokens:
            return None

        token_data = self.tokens[token]

        # Check if token is still valid
        if not token_data.get("is_valid", False):
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.utcnow() > expires_at:
            token_data["is_valid"] = False
            return None

        return token_data

    def get_token_info(self, token: str) -> Optional[dict]:
        """Get information about a token without full validation"""
        return self.tokens.get(token)
