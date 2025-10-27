import json
from typing import Dict, Any, Protocol

STATUS = "status"

class PaymentsRepository(Protocol):
    def get_all(self) -> Dict[str, Dict[str, Any]]: ...
    def get(self, payment_id: str) -> Dict[str, Any]: ...
    def upsert(self, payment_id: str, data: Dict[str, Any]) -> None: ...
    def exists(self, payment_id: str) -> bool: ...

class JsonPaymentsRepository:
    def __init__(self, path: str):
        self.path = path

    def _read(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _write(self, data: Dict[str, Dict[str, Any]]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def get_all(self):
        return self._read()

    def get(self, payment_id: str):
        data = self._read()
        if payment_id not in data:
            raise KeyError(payment_id)
        return data[payment_id]

    def upsert(self, payment_id: str, payload: Dict[str, Any]):
        data = self._read()
        data[payment_id] = payload
        self._write(data)

    def exists(self, payment_id: str) -> bool:
        return payment_id in self._read()
