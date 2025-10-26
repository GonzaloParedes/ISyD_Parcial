from typing import Dict, Any, Optional

AMOUNT = "amount"
STATUS = "status"
PAYMENT_METHOD = "payment_method"
STATUS_REGISTRADO = "REGISTRADO"

class CreditCardPayment:
    def validate(
        self,
        data: Dict[str, Any],
        *,
        context: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> bool:
        # Regla local: monto < 10.000
        try:
            v = float(data.get(AMOUNT))
        except Exception:
            return False
        if not (0 < v < 10_000):
            return False
        
        if context is None:
            return False

        current_id = data.get("id")  
        method = data.get(PAYMENT_METHOD)

        for pid, pdata in context.items():
            if current_id is not None and pid == current_id:
                continue
            if pdata.get(PAYMENT_METHOD) == method and pdata.get(STATUS) == STATUS_REGISTRADO:
                return False

        return True
