import json
from fastapi.testclient import TestClient

import main


def _write_data(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


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
 
