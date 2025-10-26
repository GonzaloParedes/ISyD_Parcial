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

def load_all_payments():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data


def save_all_payments(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_payment(payment_id):
    data = load_all_payments()[str(payment_id)]
    return data


def save_payment_data(payment_id, data):
    all_data = load_all_payments()
    all_data[str(payment_id)] = data
    save_all_payments(all_data)


def save_payment(payment_id, amount, payment_method, status):
    data = {
        AMOUNT: amount,
        PAYMENT_METHOD: payment_method,
        STATUS: status,
    }
    save_payment_data(payment_id, data)


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
    data = repo.get(str(payment_id))
    all_data = repo.get_all()

    # Copia en memoria; no afecta lo persistido
    payment_for_validation = {**data, "id": str(payment_id)}
    
    strategy = payments.get(payment_for_validation.get("payment_method"))
    ok = strategy.validate(payment_for_validation, context=all_data) if strategy else False

    payment_for_validation["status"] = "PAGADO" if ok else "FALLIDO"
    # Persistimos SIN el id extra
    updated_payment  = dict(data)
    updated_payment ["status"] = payment_for_validation["status"]
    repo.upsert(str(payment_id), updated_payment )
    return {"payment_id": payment_id, "status": payment_for_validation["status"]}

@app.post("/payments/{payment_id}/revert")
async def revert_payment(payment_id: str,repo = Depends(get_repo)):
    """
    Marca un pago como revertido (REGISTRADO si estaba FALLIDO).
    """
    data = repo.get(str(payment_id))
    estado_actual = data[STATUS]

    if estado_actual == STATUS_FALLIDO:
        data[STATUS] = STATUS_REGISTRADO

    repo.upsert(str(payment_id), data)
    return {"payment_id": payment_id, "status": data[STATUS]}

@app.get("/payments")
async def get_payments(repo = Depends(get_repo)):
    """Lista todos los pagos."""
    all_data = repo.get_all()
    return all_data
