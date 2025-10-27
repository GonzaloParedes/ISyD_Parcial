## ISyD_Parcial - Gonzalo Paredes y David Tobares - 25.10.25
## Estructura del repositorio y responsabilidades

```
├─ .github/workflows/
│  ├─ ci_pipeline.yml        # CI: corre tests automáticamente en cada PR → main
│  └─ cd_release.yml         # CD: despliegue automático al hacer merge a production
├─ clases/
│  ├─ paymentStategy.py      # (base/intefaz de estrategia de pago: patrón Strategy)
│  ├─ creditCardPayment.py   # Estrategia: reglas de Tarjeta de Crédito
│  └─ paypalPayment.py       # Estrategia: reglas de PayPal
├─ tests/
│  └─ test_payments.py       # Tests unitarios de la API y reglas de negocio
├─ .gitignore                # Archivos/Carpetas ignoradas por Git (venv, __pycache__, etc.)
├─ README.md                 # Este documento
├─ requirements.txt          # Dependencias (FastAPI, Uvicorn, PyTest, etc.)
├─ data.json                 # “Mini-DB” en JSON (persistencia simple para la demo)
├─ data_repository.py        # Se agrega data_repository el cual separa la logica de acceso a la db. Nos permite que un objeto no pueda tener acceso ilimitado a la base de datos y separar responsabilidades.
└─ main.py                   # App FastAPI: endpoints + orquestación de estrategias
```

# Descripción de la Estructura
## Main.py

Contiene la aplicación FastAPI. Define los endpoints de la API y, cuando se requiere validar/ejecutar un pago, selecciona la estrategia apropiada en función de payment_method (ej.: "credit_card", "paypal"). También gestiona la lectura/escritura de data.json como almacenamiento mínimo.

## URL de API
https://isyd-parcial.onrender.com/docs

## Data.json

Archivo JSON usado como persistencia simple (clave = payment_id). Útil para esta práctica: evita montar una base de datos. En producción se reemplazaría por una DB real.

## Data_repository.py
Se agrega el archivo data_repository el cual separa la logica de acceso a la db. Nos permite que un objeto no pueda tener acceso ilimitado a la base de datos y separar responsabilidades.

## Clases/paymentStategy.py
Define la interfaz/base del Patrón Strategy (por ej., métodos validate(...). Esto permite abrir el sistema a nuevos medios de pago sin tocar la lógica del resto de la app.

Nota: el archivo se llama paymentStategy.py

## Clases/creditCardPayment.py
Implementa la estrategia de Tarjeta de Crédito. Reglas típicas de la consigna:

Monto < 10.000.

No puede haber más de 1 pago con este medio en estado REGISTRADO.

## Clases/paypalPayment.py
Implementa la estrategia de PayPal. Regla principal:

Monto < 5.000.

## Tests/test_payments.py
Conjunto de tests unitarios (PyTest) para endpoints y/o reglas. Se ejecutan localmente con pytest -q y en CI vía GitHub Actions.

.github/workflows/ci_pipeline.yml Pipeline de CI: al crear un Pull Request hacia main, instala dependencias y ejecuta los tests. El estado de los checks aparece en el PR.

.github/workflows/cd_release.yml Pipeline de CD/Release: al hacer merge en production, corre el flujo de despliegue.

## Requirements.txt
Versiona las dependencias para que CI/CD y los entornos locales sean reproducibles.

## .gitignore
Evita commitear artefactos de entorno (ej.: .venv/, pycache/, .pytest_cache/, etc.).

## Patrón de diseño aplicado: Strategy
El núcleo de negocio usa el Patrón Strategy para encapsular la validación/ejecución por método de pago.

## ClassDiagram 

class CreditCardPayment
class PaypalPayment

PaymentStrategy <|.. CreditCardPayment
PaymentStrategy <|.. PaypalPayment

main.py --> PaymentStrategy : selecciona según payment_method

## Cómo funciona:
1. main.py recibe la request (ej.: registrar, pagar, updatear).

2. Selecciona la estrategia según payment_method.

3. Invoca validate(...)/pay(...) de la estrategia concreta.

4. Persistencia y estado se almacenan en data.json.

5. Tests verifican tanto endpoints como reglas de CreditCardPayment/PaypalPayment.

6. CI corre los tests en cada PR → main. CD despliega al hacer merge a production.
7. Se realiza el deploy a Render