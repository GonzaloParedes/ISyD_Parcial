AMOUNT = "amount"


class CreditCardPayment:
    def validate(self, data: dict) -> bool:
        # Very small simulation: valid if amount is positive and less than a large threshold
        amount = data.get(AMOUNT)
        try:
            return float(amount) > 0 and float(amount) < 100000
        except Exception:
            return False
