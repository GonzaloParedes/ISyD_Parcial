import json
from fastapi.testclient import TestClient

import main


def _write_data(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
_write = _write_data

def test_credit_card_success(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {
        "1": {"amount": 100, "payment_method": "credit_card", "status": main.STATUS_REGISTRADO}
    }
    _write_data(data_file, payload)

    main.DATA_PATH = str(data_file)

    client = TestClient(main.app)

    # act
    resp = client.post("/payments/1/pay")

    # assert
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == main.STATUS_PAGADO

    # persisted
    with open(main.DATA_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["1"]["status"] == main.STATUS_PAGADO


def test_paypal_fails_on_large_amount(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {
        "2": {"amount": 20000, "payment_method": "paypal", "status": main.STATUS_REGISTRADO}
    }
    _write_data(data_file, payload)
    main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    resp = client.post("/payments/2/pay")
    assert resp.status_code == 200
    assert resp.json()["status"] == main.STATUS_FALLIDO

    with open(main.DATA_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["2"]["status"] == main.STATUS_FALLIDO


def test_revert_from_failed(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {
        "3": {"amount": 50, "payment_method": "credit_card", "status": main.STATUS_FALLIDO}
    }
    _write_data(data_file, payload)
    main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    resp = client.post("/payments/3/revert")
    assert resp.status_code == 200
    assert resp.json()["status"] == main.STATUS_REGISTRADO

    with open(main.DATA_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["3"]["status"] == main.STATUS_REGISTRADO


def test_register_payment_success(tmp_path):
    data_file = tmp_path / "data.json"
    # start with empty store
    _write_data(data_file, {})
    main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    resp = client.post("/payments/10", params={"amount": 75, "payment_method": "credit_card"})
    assert resp.status_code == 200
    assert resp.json()["status"] == main.STATUS_REGISTRADO

    with open(main.DATA_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert "10" in d
    assert d["10"]["status"] == main.STATUS_REGISTRADO


def test_register_duplicate_fails(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {"11": {"amount": 30, "payment_method": "paypal", "status": main.STATUS_REGISTRADO}}
    _write_data(data_file, payload)
    main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    resp = client.post("/payments/11", params={"amount": 30, "payment_method": "paypal"})
    assert resp.status_code == 400


def test_update_payment_success(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {"12": {"amount": 20, "payment_method": "credit_card", "status": main.STATUS_REGISTRADO}}
    _write_data(data_file, payload)
    main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    resp = client.post("/payments/12/update", params={"amount": 150, "payment_method": "paypal"})
    assert resp.status_code == 200
    assert resp.json()["status"] == main.STATUS_REGISTRADO

    with open(main.DATA_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["12"]["amount"] == 150
    assert d["12"]["payment_method"] == "paypal"


def test_update_payment_fails_when_not_registrado(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {"13": {"amount": 20, "payment_method": "credit_card", "status": main.STATUS_PAGADO}}
    _write_data(data_file, payload)
    main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    resp = client.post("/payments/13/update", params={"amount": 50, "payment_method": "paypal"})
    assert resp.status_code == 400
 

def test_credit_card_amount_boundaries(tmp_path):
    client = TestClient(main.app)

    # Caso 0 -> FALLIDO (0 no es válido)
    data_file0 = tmp_path / "data0.json"
    _write(data_file0, {"C0": {"amount": 0, "payment_method": "credit_card", "status": main.STATUS_REGISTRADO}})
    main.DATA_PATH = str(data_file0)
    assert client.post("/payments/C0/pay").json()["status"] == main.STATUS_FALLIDO

    # Caso 9999.99 -> PAGADO (válido y único REGISTRADO)
    data_file1 = tmp_path / "data1.json"
    _write(data_file1, {"C1": {"amount": 9999.99, "payment_method": "credit_card", "status": main.STATUS_REGISTRADO}})
    main.DATA_PATH = str(data_file1)
    assert client.post("/payments/C1/pay").json()["status"] == main.STATUS_PAGADO

    # Caso 10000 -> FALLIDO (no cumple < 10000)
    data_file2 = tmp_path / "data2.json"
    _write(data_file2, {"C2": {"amount": 10000, "payment_method": "credit_card", "status": main.STATUS_REGISTRADO}})
    main.DATA_PATH = str(data_file2)
    assert client.post("/payments/C2/pay").json()["status"] == main.STATUS_FALLIDO

def test_amount_as_string_is_accepted_if_numeric(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {"S1": {"amount": "250", "payment_method": "paypal", "status": main.STATUS_REGISTRADO}}
    _write(data_file, payload); main.DATA_PATH = str(data_file)
    client = TestClient(main.app)
    assert client.post("/payments/S1/pay").json()["status"] == main.STATUS_PAGADO

def test_amount_non_numeric_fails_validation(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {"S2": {"amount": "dosmil", "payment_method": "paypal", "status": main.STATUS_REGISTRADO}}
    _write(data_file, payload); main.DATA_PATH = str(data_file)
    client = TestClient(main.app)
    assert client.post("/payments/S2/pay").json()["status"] == main.STATUS_FALLIDO

def test_missing_payment_method_fails_on_pay(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {"M1": {"amount": 100, "status": main.STATUS_REGISTRADO}}  # sin payment_method
    _write(data_file, payload); main.DATA_PATH = str(data_file)
    client = TestClient(main.app)
    assert client.post("/payments/M1/pay").json()["status"] == main.STATUS_FALLIDO

def test_get_payments_returns_all_after_operations(tmp_path):
    data_file = tmp_path / "data.json"
    payload = {
        "A": {"amount": 100, "payment_method": "credit_card", "status": main.STATUS_REGISTRADO},
        "B": {"amount": 6000, "payment_method": "paypal", "status": main.STATUS_REGISTRADO},
    }
    _write(data_file, payload); main.DATA_PATH = str(data_file)
    client = TestClient(main.app)

    client.post("/payments/A/pay")   # debería PAGAR
    client.post("/payments/B/pay")   # debería FALLAR (monto alto)
    r = client.get("/payments")
    store = r.json()
    assert store["A"]["status"] == main.STATUS_PAGADO
    assert store["B"]["status"] == main.STATUS_FALLIDO
