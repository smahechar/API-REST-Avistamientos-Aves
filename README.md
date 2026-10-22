# API REST de avistamientos de aves

Trabajo individual de Ingeniería de Software 2 (sesión 17), ampliado con pruebas unitarias y de integración en el taller de la sesión 22. API desarrollada con Python, Flask y SQLite. La base de datos se crea automáticamente al iniciar.

## Requisitos

- Python 3.10 o superior
- Visual Studio Code (recomendado)

## Instalación y ejecución

1. Abrir esta carpeta en VS Code (`Archivo > Abrir carpeta`).
2. Abrir la terminal integrada (`Terminal > Nueva terminal`).
3. Crear un entorno virtual:

   ```bash
   python -m venv .venv
   ```

4. Activar el entorno:
   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **Windows (CMD):** `.venv\Scripts\activate.bat`
   - **macOS/Linux:** `source .venv/bin/activate`

   Si PowerShell bloquea la activación, puedes usar CMD o ejecutar `.venv\Scripts\python.exe` en los comandos posteriores.

5. Instalar dependencias:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Iniciar la API:

   ```bash
   python app.py
   ```

7. Visitar `http://127.0.0.1:5000/avistamientos` en el navegador. La respuesta inicial es `[]`.

> En Windows también puedes usar `py` en vez de `python` si es necesario. En macOS/Linux puede ser `python3`.

## Endpoints y ejemplos curl

Ejecuta los comandos en **otra terminal** mientras la API está encendida. Los ejemplos usan `curl`; en PowerShell utiliza `curl.exe` para evitar conflictos con el alias `curl`.

### GET /avistamientos — listar (200)

```bash
curl http://127.0.0.1:5000/avistamientos
```

### GET /avistamientos/1 — consultar (200 o 404)

```bash
curl http://127.0.0.1:5000/avistamientos/1
```

### POST /avistamientos — crear (201 o 400)

```bash
curl -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" -d '{"especie":"colibrí","lugar":"Bogotá","fecha":"2026-09-29","observador":"Ana"}'
```

Respuesta de ejemplo (201):

```json
{"id":1,"especie":"colibrí","lugar":"Bogotá","fecha":"2026-09-29","observador":"Ana"}
```

Para probar un 400, omite `observador`.

### PUT /avistamientos/1 — actualizar (200, 400 o 404)

```bash
curl -X PUT http://127.0.0.1:5000/avistamientos/1 -H "Content-Type: application/json" -d '{"especie":"garza","lugar":"Chía","fecha":"2026-09-30","observador":"Ana"}'
```

### DELETE /avistamientos/1 — eliminar (204 o 404)

```bash
curl -X DELETE -i http://127.0.0.1:5000/avistamientos/1
```

### GET /avistamientos/resumen — bonus (200)

```bash
curl http://127.0.0.1:5000/avistamientos/resumen
```

Ejemplo de respuesta:

```json
[{"especie":"colibrí","cantidad":2},{"especie":"garza","cantidad":1}]
```

**Nota sobre PowerShell:** sus reglas de comillas pueden dificultar el envío de JSON con `curl.exe`. Puedes usar la terminal Git Bash de VS Code para copiar los comandos anteriores sin modificaciones, o usar `Invoke-RestMethod` con `-Body ($datos | ConvertTo-Json)`.

## Regla de negocio (validación)

Un avistamiento es válido si:

- `especie` tiene entre 3 y 50 caracteres (se miden sin espacios en los extremos).
- `fecha` tiene formato `AAAA-MM-DD`, existe en el calendario y no es posterior a hoy.
- `lugar` y `observador` no están vacíos.

Si no es válido, `POST` y `PUT` responden **400** con el campo que falló:

```json
{"campo": "especie", "error": "especie: debe tener entre 3 y 50 caracteres."}
```

## Estructura del código

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Capa HTTP (rutas y traducción de errores a códigos) |
| `servicio.py` | Casos de uso: coordina validador y repositorio |
| `validador.py` | Regla de negocio (`ValidadorDeAvistamiento`), lógica pura |
| `repositorio.py` | Acceso a SQLite |
| `reloj.py` | Abstracción de "hoy" (para poder usar un reloj fijo en pruebas) |

## Pruebas automatizadas

Ejecutar todas las pruebas:

```bash
python -m pytest -v
```

Solo unitarias o solo de integración:

```bash
python -m pytest tests/unit -v
python -m pytest tests/integration -v
```

Generar el reporte de cobertura (líneas y ramas) en la terminal:

```bash
python -m pytest --cov --cov-report=term-missing
```

Reporte HTML (se abre `htmlcov/index.html`):

```bash
python -m pytest --cov --cov-report=html
```

La justificación de las decisiones de prueba está en [`docs/justificacion-pruebas.md`](docs/justificacion-pruebas.md).

## Base de datos

SQLite almacena los avistamientos en `avistamientos.db`, creada automáticamente. La tabla contiene `id`, `especie`, `lugar`, `fecha` y `observador`. Las consultas usan parámetros SQL para evitar inyección SQL.

## Publicación en GitHub

Crea un repositorio público vacío en GitHub. Desde la terminal de VS Code, en esta carpeta, ejecuta:

```bash
git init
git add .
git commit -m "API REST de avistamientos de aves"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Reemplaza la URL por la de tu repositorio. Entrega el enlace público.

## Uso de IA

Se utilizó **ChatGPT (OpenAI), modelo GPT-6**, como apoyo para generar la estructura inicial, el código, las pruebas y la documentación. El estudiante debe revisar, comprender y responsabilizarse del código que publique.
