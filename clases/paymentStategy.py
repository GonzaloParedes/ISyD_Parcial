# Strategy protocol / interface for payment methods
from typing import Any, Dict, Optional


class PaymentStrategy(Protocol):
    def validate(self, data: dict,*, context: Optional[Dict[str, Any]] = None) -> bool:
        """Return True if payment is valid/successful, False otherwise."""
