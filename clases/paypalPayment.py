from typing import Dict, Any, Optional
AMOUNT = "amount"

class PaypalPayment:
    def validate(self, data: Dict[str, Any], *, context: Optional[dict] = None) -> bool:
        try:
            v = float(data.get(AMOUNT))
            return 0 < v <= 5_000
        except Exception:
            return False