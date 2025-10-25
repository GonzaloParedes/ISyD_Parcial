AMOUNT = "amount"


class PaypalPayment:
    def validate(self, data: dict) -> bool:
        # Simulated rule: paypal fails if amount is over 10000 (for this example)
        amount = data.get(AMOUNT)
        try:
            return float(amount) > 0 and float(amount) <= 10000
        except Exception:
            return False