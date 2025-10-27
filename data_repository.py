import json
from typing import Dict, Any, Protocol
import os, tempfile, shutil

STATUS = "status"

class PaymentsRepository(Protocol):
    def get_all(self) -> Dict[str, Dict[str, Any]]: ...
    def get(self, payment_id: str) -> Dict[str, Any]: ...
    def upsert(self, payment_id: str, data: Dict[str, Any]) -> None: ...
    def exists(self, payment_id: str) -> bool: ...

class JsonPaymentsRepository:
    def __init__(self, path: str):
        self.path = path

    def _ensure_store(self) -> None:
        """Crea el archivo (y carpeta) si no existe; si está corrupto, lo resetea."""
        folder = os.path.dirname(self.path) or "."
        os.makedirs(folder, exist_ok=True)
        if not os.path.exists(self.path):
            self._write({})
            return
        # archivo existe: validemos que tenga JSON válido
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception:
            # backup y reseteo
            try:
                shutil.copyfile(self.path, f"{self.path}.bak")
            except Exception:
                pass
            self._write({})

    def _read(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            # si por algún motivo se borró en runtime: recreamos
            self._write({})
            return {}
        except Exception:
            # corrupción en caliente
            try:
                shutil.copyfile(self.path, f"{self.path}.bak")
            except Exception:
                pass
            self._write({})
            return {}

    def _write(self, data: Dict[str, Dict[str, Any]]) -> None:
        # escritura atómica para evitar cortes a mitad
        dir_ = os.path.dirname(self.path) or "."
        fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".data.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass
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
