import json
from fastapi import FastAPI, HTTPException, Depends
from typing import Protocol

from clases.creditCardPayment import CreditCardPayment
from clases.paypalPayment import PaypalPayment
from data_repository import JsonPaymentsRepository

STATUS = "status"
AMOUNT = "amount"
PAYMENT_METHOD = "payment_method"
STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"
DATA_PATH = "data.json"
# Registry of available payment strategies
payments = {
    "credit_card": CreditCardPayment(),
    "paypal": PaypalPayment(),
}

app = FastAPI()

def get_repo():
    return JsonPaymentsRepository(DATA_PATH)

@app.get("/payments")
async def get_payments(repo = Depends(get_repo)):
    """Lista todos los pagos."""
    all_data = repo.get_all()
    return all_data

@app.post("/payments/{payment_id}")
async def register_payment(payment_id: str, amount: float, payment_method: str,repo = Depends(get_repo)):
    """Registrar: crea un pago nuevo en estado REGISTRADO.

    Si el payment_id ya existe devuelve 400.
    """
    all_data = repo.get_all()
    if str(payment_id) in all_data:
        raise HTTPException(status_code=400, detail="payment_id already exists")

    payload = {AMOUNT: amount, PAYMENT_METHOD: payment_method, STATUS: STATUS_REGISTRADO}
    repo.upsert(str(payment_id), payload)
    return {"payment_id": payment_id, "status": STATUS_REGISTRADO}


@app.post("/payments/{payment_id}/update")
async def update_payment(payment_id: str, amount: float, payment_method: str,repo = Depends(get_repo)):
    """Actualiza la información de un pago existente.

    Solo permite actualizar si el pago existe y está en estado REGISTRADO.
    """
    all_data = repo.get_all()
    if str(payment_id) not in all_data:
        raise HTTPException(status_code=404, detail="payment_id not found")

    data = all_data[str(payment_id)]
    if data.get(STATUS) != STATUS_REGISTRADO:
        raise HTTPException(status_code=400, detail="Only REGISTRADO payments can be updated")

    data[AMOUNT] = amount
    data[PAYMENT_METHOD] = payment_method
    repo.upsert(str(payment_id), data)
    return {"payment_id": payment_id, "status": data[STATUS]}

@app.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: str, repo = Depends(get_repo)):
    """Intenta pagar un registro aplicando la validación del método."""
    try:
        current_payment = repo.get(str(payment_id))
    except KeyError:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    all_payments = repo.get_all()

    # Copia en memoria para validación (no se persiste 'id')
    payment_for_validation = {**current_payment, "id": str(payment_id)}

    method = payment_for_validation.get(PAYMENT_METHOD)          # usar constante
    strategy = payments.get(method)
    is_valid = strategy.validate(payment_for_validation, context=all_payments) if strategy else False

    updated = dict(current_payment)
    updated[STATUS] = STATUS_PAGADO if is_valid else STATUS_FALLIDO
    repo.upsert(str(payment_id), updated)
    return {"payment_id": payment_id, "status": updated[STATUS]}

@app.post("/payments/{payment_id}/revert")
async def revert_payment(payment_id: str,repo = Depends(get_repo)):
    """
    Marca un pago como revertido (REGISTRADO si estaba FALLIDO).
    """
    try:
        data = repo.get(str(payment_id))
    except KeyError:
        raise HTTPException(status_code=404, detail="payment_id not found")

    # Idempotente: solo cambia FALLIDO -> REGISTRADO, si no, se mantiene
    if data.get(STATUS) == STATUS_FALLIDO:
        data[STATUS] = STATUS_REGISTRADO
        repo.upsert(str(payment_id), data)

    return {"payment_id": payment_id, "status": data[STATUS]}

