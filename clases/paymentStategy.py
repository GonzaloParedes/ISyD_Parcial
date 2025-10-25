# Strategy protocol / interface for payment methods
class PaymentStrategy(Protocol):
    def validate(self, data: dict) -> bool:
        """Return True if payment is valid/successful, False otherwise."""
