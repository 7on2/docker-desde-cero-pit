# Laboratorios de Volúmenes Docker

## Objetivo

Aprender a persistir datos en Docker usando volúmenes nombrados, bind mounts y backups.

---

## Lab 1: Volumen Nombrado para PostgreSQL

### Objetivo

Persistir datos de PostgreSQL aunque se elimine el contenedor.

### Paso 1: Crear volumen

```bash
docker volume create pgdata
```

Verificar:

```bash
docker volume ls
```

Inspeccionar:

```bash
docker volume inspect pgdata
```

Salida esperada:

```json
[
  {
    "Name": "pgdata",
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/pgdata/_data"
  }
]
```

### Paso 2: Lanzar PostgreSQL con volumen

```bash
docker run -d \
  --name db \
  --network app-net \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=appdb \
  postgres:16
```

Explicación:

```text
-v pgdata:/var/lib/postgresql/data
```

Todo lo que PostgreSQL escriba en `/var/lib/postgresql/data` quedará guardado en el volumen `pgdata`.

### Paso 3: Insertar datos de prueba

```bash
docker exec -i db psql -U appuser -d appdb << 'SQL'
CREATE TABLE clientes (id SERIAL PRIMARY KEY, nombre TEXT, email TEXT);
INSERT INTO clientes (nombre, email) VALUES
  ('Ana Torres', 'ana@empresa.com'),
  ('Carlos Ruiz', 'carlos@empresa.com'),
  ('María López', 'maria@empresa.com');
SELECT * FROM clientes;
SQL
```

### Paso 4: Eliminar el contenedor

```bash
docker stop db && docker rm db
```

Verificar que el volumen sigue existiendo:

```bash
docker volume ls | grep pgdata
```

### Paso 5: Recrear PostgreSQL con el mismo volumen

```bash
docker run -d \
  --name db \
  --network app-net \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=appdb \
  postgres:16
```

### Paso 6: Verificar que los datos persistieron

```bash
docker exec db psql -U appuser -d appdb -c "SELECT * FROM clientes;"
```

**Salida esperada:** Los 3 registros siguen ahí. El volumen `pgdata` preservó los datos aunque el contenedor se destruyó.

---

## Lab 2: Docker Compose con Flask + PostgreSQL + Volumen

### Objetivo

Levantar una app Flask y PostgreSQL usando Compose con volumen nombrado.

### Paso 1: Crear carpeta

```bash
mkdir -p lab2-compose-postgres
cd lab2-compose-postgres
```

### Paso 2: Crear app.py

```bash
cat > app.py << 'EOF'
import os
import time
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "appdb")
DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "apppass")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def wait_for_db():
    for intento in range(1, 11):
        try:
            conn = get_conn()
            conn.close()
            print("PostgreSQL listo")
            return
        except Exception as error:
            print(f"Intento {intento}/10: DB no lista: {error}")
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a PostgreSQL")

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitas (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO visitas DEFAULT VALUES;")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM visitas;")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    return jsonify({
        "mensaje": "Flask conectado a PostgreSQL usando Docker Compose",
        "db_host": DB_HOST,
        "visitas": total
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=5000)
EOF
```

### Paso 3: Crear requirements.txt

```bash
cat > requirements.txt << 'EOF'
Flask==3.0.3
psycopg2-binary==2.9.9
EOF
```

### Paso 4: Crear Dockerfile

```bash
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

### Paso 5: Crear compose.yaml

```bash
cat > compose.yaml << 'EOF'
services:
  db:
    image: postgres:16
    container_name: lab2-db
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  app:
    build: .
    container_name: lab2-app
    environment:
      DB_HOST: db
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    ports:
      - "5001:5000"
    networks:
      - backend
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:

networks:
  backend:
EOF
```

Explicación:

```yaml
volumes:
  - pgdata:/var/lib/postgresql/data
```

Guarda datos de PostgreSQL en un volumen.

```yaml
depends_on:
  db:
    condition: service_healthy
```

La app espera a que la base esté saludable.

### Paso 6: Levantar el proyecto

```bash
docker compose up -d --build
```

Ver servicios:

```bash
docker compose ps
```

Salida esperada:

```text
lab2-db    healthy
lab2-app   running
```

### Paso 7: Probar la app

```bash
curl http://localhost:5001
```

Ejecutar varias veces:

```bash
curl http://localhost:5001
curl http://localhost:5001
curl http://localhost:5001
```

La cantidad de visitas debe aumentar.

### Paso 8: Ver datos directamente en PostgreSQL

```bash
docker compose exec db psql -U appuser -d appdb -c "SELECT * FROM visitas;"
```

### Paso 9: Insertar tabla clientes

```bash
docker compose exec -T db psql -U appuser -d appdb << 'SQL'
CREATE TABLE IF NOT EXISTS clientes (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  email TEXT NOT NULL
);

INSERT INTO clientes (nombre, email) VALUES
('Ana Torres', 'ana@empresa.com'),
('Carlos Ruiz', 'carlos@empresa.com');

SELECT * FROM clientes;
SQL
```

### Paso 10: Backup con pg_dump

Crear carpeta si no existe:

```bash
mkdir -p backups
```

Generar backup:

```bash
docker compose exec -T db pg_dump -U appuser appdb > backups/appdb.sql
```

Verificar:

```bash
ls -lh backups/
head -20 backups/appdb.sql
```

### Paso 11: Probar persistencia del volumen

Apagar sin borrar volumen:

```bash
docker compose down
```

Levantar otra vez:

```bash
docker compose up -d
```

Consultar datos:

```bash
docker compose exec db psql -U appuser -d appdb -c "SELECT * FROM clientes;"
```

Los datos deben seguir ahí.

Explicación:

```text
docker compose down
```

Elimina contenedores y red del proyecto, pero no elimina el volumen por defecto.

### Paso 12: Borrar todo incluyendo volumen

Solo al final:

```bash
docker compose down -v
```

Advertencia:

```text
-v elimina el volumen pgdata.
Eso borra los datos de PostgreSQL.
```

---

## Lab 3: Nginx + Flask + PostgreSQL con Volumen

### Objetivo

Crear una arquitectura más parecida a producción con Nginx como reverse proxy.

### Paso 1: Crear carpeta

```bash
mkdir -p lab3-nginx-proxy
cd lab3-nginx-proxy
mkdir -p nginx
```

### Paso 2: Crear app.py

```bash
cat > app.py << 'EOF'
import os
import time
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "appdb")
DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "apppass")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def wait_for_db():
    for intento in range(1, 11):
        try:
            conn = get_conn()
            conn.close()
            print("DB lista")
            return
        except Exception as error:
            print(f"Intento {intento}/10: {error}")
            time.sleep(2)
    raise RuntimeError("DB no disponible")

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitas_proxy (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO visitas_proxy DEFAULT VALUES;")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM visitas_proxy;")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    return jsonify({
        "mensaje": "Respuesta generada por Flask detras de Nginx",
        "flujo": "Host -> Nginx -> Flask -> PostgreSQL",
        "db_host": DB_HOST,
        "visitas_proxy": total
    })

@app.route("/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as error:
        return jsonify({"status": "error", "detalle": str(error)}), 500

if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=5000)
EOF
```

### Paso 3: Crear requirements.txt

```bash
cat > requirements.txt << 'EOF'
Flask==3.0.3
psycopg2-binary==2.9.9
gunicorn==22.0.0
EOF
```

### Paso 4: Crear Dockerfile multi-stage

```bash
cat > Dockerfile << 'EOF'
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
EOF
```

### Paso 5: Crear configuración de Nginx

```bash
cat > nginx/default.conf << 'EOF'
server {
    listen 80;

    location / {
        proxy_pass http://app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
```

### Paso 6: Crear compose.yaml

```bash
cat > compose.yaml << 'EOF'
services:
  db:
    image: postgres:16
    container_name: lab3-db
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    volumes:
      - dbdata:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: lab3-app
    environment:
      DB_HOST: db
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    expose:
      - "5000"
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy

  nginx:
    image: nginx:1.27-alpine
    container_name: lab3-nginx
    ports:
      - "8080:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - frontend
    depends_on:
      - app

volumes:
  dbdata:

networks:
  frontend:
  backend:
EOF
```

### Paso 7: Levantar arquitectura

```bash
docker compose up -d --build
```

Ver estado:

```bash
docker compose ps
```

Salida esperada:

```text
lab3-db       healthy
lab3-app      running
lab3-nginx    running
```

### Paso 8: Probar desde el host

```bash
curl http://localhost:8080
```

Salida esperada:

```json
{
  "db_host": "db",
  "flujo": "Host -> Nginx -> Flask -> PostgreSQL",
  "mensaje": "Respuesta generada por Flask detras de Nginx",
  "visitas_proxy": 1
}
```

### Paso 9: Comprobar que Flask no está publicado

```bash
curl http://localhost:5000
```

Debe fallar.

### Paso 10: Ver volumen

```bash
docker volume ls
docker volume inspect lab3-nginx-proxy_dbdata
```

El nombre real del volumen puede cambiar según la carpeta.

### Paso 11: Apagar sin borrar volumen

```bash
docker compose down
```

### Paso 12: Borrar incluyendo volumen

```bash
docker compose down -v
```

---

## Comandos Útiles de Volúmenes

| Comando | Descripción |
|---------|-------------|
| `docker volume create <nombre>` | Crear un volumen |
| `docker volume ls` | Listar todos los volúmenes |
| `docker volume inspect <nombre>` | Ver detalles de un volumen |
| `docker volume rm <nombre>` | Eliminar un volumen |
| `docker volume prune` | Eliminar volúmenes sin usar |
| `-v <volumen>:<ruta>` | Montar volumen en un contenedor |
| `-v $(pwd):<ruta>` | Bind mount de carpeta local |
| `docker compose down` | Eliminar contenedores y redes (conserva volúmenes) |
| `docker compose down -v` | Eliminar contenedores, redes y volúmenes |

---

## Errores Frecuentes

| Error | Causa | Solución |
|-------|-------|----------|
| Datos desaparecen | Falta volumen nombrado | Agregar `-v pgdata:/var/lib/postgresql/data` |
| App no conecta a BD | Host incorrecto | Usar `DB_HOST=db` |
| BD expuesta al host | Se agregó `ports` en `db` | Quitar `ports` si no hace falta |
| Healthcheck no pasa | Usuario o base incorrectos | Revisar variables de entorno |
| Backup vacío o falla | Servicio `db` no está listo | Revisar `docker compose ps` |
| Volumen no se elimina | Contenedor aún activo | Detener contenedor primero |
| Nombre de volumen incorrecto | Compose agrega prefijo | Usar `docker volume ls | grep <nombre>` |
