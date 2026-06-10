# LAB 2 — Dockerfile y Construcción de Imágenes Custom

En este laboratorio construiremos nuestra propia imagen Docker usando Dockerfile. Reutilizamos la aplicación de gestión de tareas (Flask + PostgreSQL + Nginx) del curso para que el contexto sea familiar.

## Objetivo

- Entender todas las instrucciones del Dockerfile y cuándo usarlas.
- Construir imágenes con `docker build` y optimizar el caché.
- Crear una imagen multi-stage para reducir tamaño.
- Escribir un `.dockerignore` para excluir archivos innecesarios.

---

## Estructura del proyecto

```
lab2/
├── Dockerfile          ← imagen de la app Flask
├── Dockerfile.multistage ← imagen optimizada multi-stage
├── .dockerignore       ← archivos a excluir del contexto
├── requirements.txt    ← dependencias Python
└── app/
    ├── app.py          ← código de la aplicación Flask
    └── templates/
        └── index.html  ← plantilla HTML
```

---

## Paso 1 — Archivos de la aplicación

### 1.1 Archivo `requirements.txt`

Lista las librerías Python que necesita la aplicación:

```text
Flask==3.0.3
psycopg2-binary==2.9.9
python-dotenv==1.0.1
gunicorn==22.0.0
```

| Librería | Rol |
|----------|-----|
| `Flask` | Framework web. Nuestro servidor HTTP. |
| `psycopg2-binary` | Driver para conectarse a PostgreSQL desde Python. |
| `python-dotenv` | Carga variables de entorno desde un archivo `.env`. |
| `gunicorn` | Servidor WSGI de producción para Flask. |

### 1.2 Código de la app (`app.py`)

La app expone endpoints REST que se conectan a PostgreSQL:

- `GET /` — lista todas las tareas
- `POST /tareas` — crea una tarea nueva
- `DELETE /tareas/<id>` — elimina una tarea
- `GET /health` — healthcheck endpoint

> La app requiere las variables de entorno `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS` para conectarse a PostgreSQL. Se completan en el Lab 3 con Docker Compose.

---

## Paso 2 — Escribir el Dockerfile

### 2.1 Versión completa comentada

```dockerfile
FROM python:3.11-slim

LABEL maintainer="tony@uni.edu.pe"
LABEL description="Gestor de Tareas - Docker Labs UNI"
LABEL version="1.0"

ARG APP_PORT=5000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=${APP_PORT}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

| Instrucción | Explicación |
|-------------|-------------|
| `FROM python:3.11-slim` | Imagen base. `slim` = sin herramientas de compilación, más liviana. |
| `LABEL` | Metadatos informativos. Se ven con `docker image inspect`. |
| `ARG APP_PORT=5000` | Variable solo disponible durante el BUILD. Sobreescribible con `--build-arg`. |
| `ENV` | Variable de entorno disponible en RUNTIME también. |
| `WORKDIR /app` | Directorio de trabajo. Si no existe, Docker lo crea. |
| `COPY requirements.txt .` | PRIMERO copiamos solo requirements.txt (cache optimization). |
| `RUN pip install` | Instalar dependencias. `--no-cache-dir` ahorra espacio. |
| `COPY app/ .` | Copiamos el código DESPUÉS de instalar deps (no invalida caché de pip). |
| `USER appuser` | Usuario no-root. Buena práctica de seguridad. |
| `EXPOSE 5000` | Documentar puerto. NO lo abre, es informativo. |
| `HEALTHCHECK` | Docker verifica la salud del contenedor periódicamente. |
| `CMD ["gunicorn", ...]` | Comando por defecto al iniciar. Exec form (JSON) evita shell intermedio. |

### 2.2 Archivo `.dockerignore`

```
__pycache__/
*.pyc
*.pyo
.git/
.gitignore

venv/
.venv/
env/

.env
*.key
*.pem

docs/
tests/
README.md

.vscode/
.idea/
```

---

## Paso 3 — Construir la imagen con `docker build`

```bash
cd ~/lab2

docker build -t gestor-tareas:v1.0 .
docker build --no-cache -t gestor-tareas:v1.0 .
docker build --build-arg APP_PORT=8000 -t gestor-tareas:v1.1 .

docker images | grep gestor-tareas
docker history gestor-tareas:v1.0
docker image inspect gestor-tareas:v1.0 --format '{{.Size}}'
```

| Opción | Explicación |
|--------|-------------|
| `docker build -t <name>:<tag> .` | El punto es el **BUILD CONTEXT**: directorio desde donde Docker lee los archivos. |
| `--no-cache` | Fuerza reconstrucción de todas las capas. |
| `--build-arg CLAVE=valor` | Sobreescribe una variable `ARG` definida en el Dockerfile. |
| `docker history <image>` | Muestra cada capa: tamaño, instrucción. |

---

## Paso 4 — Entendiendo el Sistema de Caché

Cada instrucción genera una capa. Si la instrucción y su contexto no cambian, Docker reutiliza la capa cacheada.

```bash
docker build -t gestor-tareas:cache-test .
echo '# cambio' >> app/app.py
docker build -t gestor-tareas:cache-test .
# Observar: las líneas con 'CACHED' = capa reutilizada
```

> **TIP:** El orden de instrucciones importa para el caché. Siempre copia lo que cambia **menos** primero (`requirements.txt`) y lo que cambia **más** al final (código fuente).

---

## Paso 5 — Multi-Stage Build (Optimización)

Un multi-stage build usa múltiples `FROM` en el mismo Dockerfile. Las etapas anteriores se usan para compilar/construir, y solo la última se convierte en la imagen final.

```dockerfile
# ═══ STAGE 1: builder ═══
FROM python:3.11 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# ═══ STAGE 2: runtime ═══
FROM python:3.11-slim AS runtime
LABEL maintainer="tony@uni.edu.pe"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps
WORKDIR /app
COPY --from=builder /install ./deps
COPY app/ .
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1
CMD ["python", "-m", "gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -f Dockerfile.multistage -t gestor-tareas:slim .
```

| Concepto | Explicación |
|----------|-------------|
| `FROM python:3.11 AS builder` | Primera etapa: tiene pip y herramientas completas. |
| `COPY --from=builder /install ./deps` | Solo copia las dependencias instaladas, no pip ni compiladores. |
| `FROM python:3.11-slim AS runtime` | Segunda etapa: imagen final, mucho más pequeña. |
| `-f Dockerfile.multistage` | Especifica qué Dockerfile usar cuando no se llama `Dockerfile`. |

---

## Resumen del Laboratorio 2

| Instrucción / Comando | Función |
|----------------------|---------|
| `FROM / LABEL / ARG / ENV` | Base, metadatos y variables del Dockerfile. |
| `WORKDIR / COPY / RUN` | Directorio de trabajo, copiar archivos y ejecutar comandos. |
| `USER / EXPOSE / HEALTHCHECK` | Seguridad, documentación de puertos y monitoreo de salud. |
| `docker build -t` | Construir una imagen desde un Dockerfile. |
| `docker history <image>` | Ver capas y tamaños. |
| `.dockerignore` | Excluir archivos del contexto de build. |
| Multi-stage build | Reducir tamaño de imagen separando build de runtime. |