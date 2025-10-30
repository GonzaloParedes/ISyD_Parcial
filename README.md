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
├─ README.md                 # Este documento muestra la documentación de nuestro proyecto 
├─ requirements.txt          # Dependencias
├─ data.json                 # “Mini-DB” en JSON (persistencia simple para la demo)
├─ data_repository.py        # Se agrega data_repository el cual separa la logica de acceso a la db. Nos permite que un objeto no pueda tener acceso ilimitado a la base de datos y separar responsabilidades.
└─ main.py                   # App FastAPI: endpoints
```

# Descripción de la Estructura
## Main.py

Contiene la aplicación FastAPI. Define los endpoints de la API y, cuando se requiere validar/ejecutar un pago, selecciona la estrategia apropiada en función de payment_method (ej.: "credit_card", "paypal"). 

## URL de API
https://isyd-parcial.onrender.com/docs

## Data.json

Archivo JSON usado como persistencia simple (clave = payment_id). Útil para esta práctica: evita montar una base de datos. En un entorno productivo real se reemplazaría por una DB real.

## Data_repository.py
Se agrega el archivo data_repository el cual separa la logica de acceso a la db. Nos permite que un objeto no pueda tener acceso ilimitado a la base de datos y separar responsabilidades. Se encarga de lectura y escritura de datos. 

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
Conjunto de tests unitarios (PyTest) para endpoints y/o reglas. Se ejecutan localmente con pytest -q desde el root del proyecto y en CI vía GitHub Actions.

.github/workflows/ci_pipeline.yml Pipeline de CI: al crear un Pull Request hacia main, instala dependencias y ejecuta los tests. El estado de los checks aparece en el PR.

.github/workflows/cd_release.yml Pipeline de CD/Release: al hacer merge en production, corre el flujo de despliegue.

## Requirements.txt
Versiona las dependencias para que CI/CD y los entornos locales sean reproducibles.

## .gitignore
Evita commitear artefactos de entorno (ej.: .venv/, pycache/, .pytest_cache/, etc.).

## Patrón de diseño aplicado: Strategy
El núcleo de negocio usa el Patrón Strategy para encapsular la validación/ejecución por método de pago.
Ya que al momento de revisar la consigna, pensamos en poder usar Chain of responsability y patrón State; pero debido a la complejidad del problema, nos llevaría más tiempo para analizar el desarrollo del patrón (del cual no estamos muy familiarizados en la práctica). 
En contraposición con el patrón Strategy, ya visto en clase. 

## Validación de los pagos: 

![alt text](image.png)


## Realización de los deploys: 

Tenemos 2 ramas principales: 
Main y Production.

En main mergeamos el código aprobado. 
En rama Production se encuentra el código que esta en producción. Render está configurado para desplegar automáticamente, cada vez que Production se modifique. 

Al querer emitir una nueva versión a Production; se realiza merge de lo que queremos actualizar en Main; y creamos un tag sobre ese commit de main. 
Cuando se sube el Tag, nuestro workflow genera un release de GitHub con su Tag asociado. Y mueve el código de main a production branch.  



