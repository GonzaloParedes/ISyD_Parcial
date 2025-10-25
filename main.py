'''
import json
from fastapi import FastAPI, HTTPException
from typing import Protocol

from clases.creditCardPayment import CreditCardPayment
from clases.paypalPayment import PaypalPayment


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
async def register_payment(payment_id: str, amount: float, payment_method: str):
    """Registrar: crea un pago nuevo en estado REGISTRADO.

    Si el payment_id ya existe devuelve 400.
    """
    all_data = load_all_payments()
    if str(payment_id) in all_data:
        raise HTTPException(status_code=400, detail="payment_id already exists")

    save_payment(payment_id, amount, payment_method, STATUS_REGISTRADO)
    return {"payment_id": payment_id, "status": STATUS_REGISTRADO}


@app.post("/payments/{payment_id}/update")
async def update_payment(payment_id: str, amount: float, payment_method: str):
    """Actualiza la información de un pago existente.

    Solo permite actualizar si el pago existe y está en estado REGISTRADO.
    """
    all_data = load_all_payments()
    if str(payment_id) not in all_data:
        raise HTTPException(status_code=404, detail="payment_id not found")

    data = all_data[str(payment_id)]
    if data.get(STATUS) != STATUS_REGISTRADO:
        raise HTTPException(status_code=400, detail="Only REGISTRADO payments can be updated")

    data[AMOUNT] = amount
    data[PAYMENT_METHOD] = payment_method

    save_payment_data(payment_id, data)
    return {"payment_id": payment_id, "status": data[STATUS]}

@app.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: str):
    """
    Marca un pago como pagado (o FALLIDO si la validación falla).
    """
    data = load_payment(payment_id)
    method = data.get(PAYMENT_METHOD)

    strategy = payments.get(method)
    if strategy is None:
        # Unknown payment method -> mark as failed
        data[STATUS] = STATUS_FALLIDO
    else:
        success = strategy.validate(data)
        data[STATUS] = STATUS_PAGADO if success else STATUS_FALLIDO

    # persist the updated status
    save_payment_data(payment_id, data)

    # return the updated status to the caller
    return {"payment_id": payment_id, "status": data[STATUS]}


@app.post("/payments/{payment_id}/revert")
async def revert_payment(payment_id: str):
    """
    Marca un pago como revertido (REGISTRADO si estaba FALLIDO).
    """
    data = load_payment(payment_id)
    estado_actual = data[STATUS]

    if estado_actual == STATUS_FALLIDO:
        data[STATUS] = STATUS_REGISTRADO

    save_payment_data(payment_id, data)
    return {"payment_id": payment_id, "status": data[STATUS]}




@app.post("/path/{arg_1}/some_action")
async def endpoint_b(arg_1: str, arg_2: float, arg_3: str):
    # Este es un endpoint POST que recibe un argumento (arg_1) por path y otros dos por query (arg_2 y arg_3).
    return {}
“””
'''

import json, os
from fastapi import FastAPI

DATA_PATH = "data.json"

app = FastAPI(title="Payments API", version="0.1.0")

def read_db() -> dict:
    """Devuelve el contenido de data.json como dict. Crea {} si no existe/corrupto."""
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)
    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

@app.get("/payments")
async def get_payments():
    """Lista todos los pagos."""
    return read_db()
