# ISyD_Parcial

### Estructura del repositorio y responsabilidades
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
└─ main.py                   # App FastAPI: endpoints + orquestación de estrategias

## Descripción rápida

# main.py
Contiene la aplicación FastAPI. Define los endpoints de la API y, cuando se requiere validar/ejecutar un pago, selecciona la estrategia apropiada en función de payment_method (ej.: "credit_card", "paypal"). También gestiona la lectura/escritura de data.json como almacenamiento mínimo.

# data.json
Archivo JSON usado como persistencia simple (clave = payment_id). Útil para la práctica: evita montar una base de datos. En producción se reemplazaría por una DB real.

# clases/paymentStategy.py
Define la interfaz/base del Patrón Strategy (por ej., métodos validate(...) y/o pay(...)). Esto permite abrir el sistema a nuevos medios de pago sin tocar la lógica del resto de la app (principio OCP).

Nota: el archivo se llama paymentStategy.py (sin “r”). Si el equipo lo prefiere, conviene renombrarlo a paymentStrategy.py para claridad, ajustando los imports.

# clases/creditCardPayment.py
Implementa la estrategia de Tarjeta de Crédito. Reglas típicas de la consigna:

Monto < 10.000.

No puede haber más de 1 pago con este medio en estado REGISTRADO.

# clases/paypalPayment.py
Implementa la estrategia de PayPal. Regla principal:

Monto < 5.000.

# tests/test_payments.py
Conjunto de tests unitarios (PyTest) para endpoints y/o reglas. Se ejecutan localmente con pytest -q y en CI vía GitHub Actions.

.github/workflows/ci_pipeline.yml
Pipeline de CI: al crear un Pull Request hacia main, instala dependencias y ejecuta los tests. El estado de los checks aparece en el PR.

.github/workflows/cd_release.yml
Pipeline de CD/Release: al hacer merge en production, corre el flujo de despliegue (por ejemplo vía SSH o al proveedor elegido). Requiere secrets configurados en Settings → Actions → Secrets.

# requirements.txt
Versiona las dependencias para que CI/CD y los entornos locales sean reproducibles.

# .gitignore
Evita commitear artefactos de entorno (ej.: .venv/, __pycache__/, .pytest_cache/, etc.).

### Patrón de diseño aplicado: Strategy

El núcleo de negocio usa el Patrón Strategy para encapsular la validación/ejecución por método de pago.

classDiagram
    class PaymentStrategy {
      +validate(amount, context) bool
      +pay(context) -> status
    }

    class CreditCardPayment
    class PaypalPayment

    PaymentStrategy <|.. CreditCardPayment
    PaymentStrategy <|.. PaypalPayment

    main.py --> PaymentStrategy : selecciona según payment_method

### Cómo se conectan las piezas (vista rápida)

main.py recibe la request (ej.: registrar, pagar, updatear).

Selecciona la estrategia según payment_method.

Invoca validate(...)/pay(...) de la estrategia concreta.

Persistencia y estado se almacenan en data.json.

Tests verifican tanto endpoints como reglas de CreditCardPayment/PaypalPayment.

CI corre los tests en cada PR → main.
CD despliega al hacer merge a production.
