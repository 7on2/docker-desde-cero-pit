# Laboratorios de Volúmenes Docker

## Objetivo

Aprender a persistir datos en Docker usando volúmenes nombrados, bind mounts y backups.

---

## Ejercicio 1: PostgreSQL sin volumen vs con volumen

### Objetivo

Demostrar que los datos escritos dentro de un contenedor se pierden si el contenedor se elimina, y que un volumen nombrado resuelve ese problema.

### Parte A: PostgreSQL sin volumen

#### Paso 1: crear carpeta

```bash
mkdir -p ejercicio01a-postgres-sin-volumen
cd ejercicio01a-postgres-sin-volumen
```

#### Paso 2: crear docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: pitdb
      POSTGRES_USER: pituser
      POSTGRES_PASSWORD: pitpass
EOF
```

No existe sección `volumes`. Los datos quedarán dentro del filesystem del contenedor.

#### Paso 3: levantar e insertar datos

```bash
docker compose up -d

docker compose exec db psql -U pituser -d pitdb -c \
  "CREATE TABLE notas (id SERIAL PRIMARY KEY, texto TEXT);"

docker compose exec db psql -U pituser -d pitdb -c \
  "INSERT INTO notas (texto) VALUES ('dato sin volumen');"

docker compose exec db psql -U pituser -d pitdb -c \
  "SELECT * FROM notas;"
```

La tabla y el dato existen mientras el contenedor existe.

#### Paso 4: eliminar y recrear

```bash
docker compose down
docker compose up -d

docker compose exec db psql -U pituser -d pitdb -c \
  "SELECT * FROM notas;"
```

El `SELECT` debe fallar con un error similar a `relation "notas" does not exist`. La tabla se perdió porque el contenedor anterior fue eliminado.

#### Paso 5: limpiar

```bash
docker compose down
```

### Parte B: PostgreSQL con volumen nombrado

#### Paso 1: crear carpeta

```bash
cd ..
mkdir -p ejercicio01b-postgres-con-volumen
cd ejercicio01b-postgres-con-volumen
```

#### Paso 2: crear docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: pitdb
      POSTGRES_USER: pituser
      POSTGRES_PASSWORD: pitpass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
EOF
```

`pgdata` es un volumen nombrado administrado por Docker. Se monta en `/var/lib/postgresql/data`, que es la ruta donde PostgreSQL guarda sus datos.

#### Paso 3: levantar e insertar datos

```bash
docker compose up -d

docker compose exec db psql -U pituser -d pitdb -c \
  "CREATE TABLE notas (id SERIAL PRIMARY KEY, texto TEXT);"

docker compose exec db psql -U pituser -d pitdb -c \
  "INSERT INTO notas (texto) VALUES ('dato con volumen');"

docker compose exec db psql -U pituser -d pitdb -c \
  "SELECT * FROM notas;"
```

#### Paso 4: eliminar y recrear conservando volumen

```bash
docker compose down
docker compose up -d

docker compose exec db psql -U pituser -d pitdb -c \
  "SELECT * FROM notas;"
```

El dato debe seguir existiendo. El contenedor se eliminó, pero el volumen sobrevivió.

#### Paso 5: ver volúmenes

```bash
docker volume ls
docker volume inspect ejercicio01b-postgres-con-volumen_pgdata
```

Compose prefija el volumen con el nombre del proyecto. Por eso el volumen real puede llamarse `ejercicio01b-postgres-con-volumen_pgdata`.

#### Paso 6: borrar también el volumen

```bash
docker compose down -v
```

`down -v` elimina los datos persistentes. Debe usarse solo cuando se quiere reiniciar la base desde cero.

---

## Ejercicio 2: Bind mount para desarrollo en vivo

### Objetivo

Montar un archivo local dentro de un contenedor para modificar código sin reconstruir la imagen cada vez.

Un bind mount conecta una ruta del host con una ruta del contenedor. Es útil en desarrollo porque el editor modifica el archivo local y el contenedor ve el cambio.

### Paso 1: crear carpeta del ejercicio

```bash
mkdir -p ejercicio02-bind-mount
cd ejercicio02-bind-mount
```

### Paso 2: crear app.py

```bash
cat > app.py << 'EOF'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"version": "1.0", "mensaje": "Codigo montado con bind mount"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
EOF
```

### Paso 3: crear Dockerfile

```bash
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.3

COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
EOF
```

El Dockerfile copia `app.py`, pero en desarrollo el bind mount lo reemplazará por el archivo local.

### Paso 4: crear docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
services:
  web:
    build: .
    ports:
      - "5001:5000"
    volumes:
      - ./app.py:/app/app.py
EOF
```

La línea `./app.py:/app/app.py` significa: archivo local `app.py` montado sobre el archivo `/app/app.py` dentro del contenedor.

### Paso 5: levantar y probar

```bash
docker compose up -d --build
curl http://localhost:5001/
```

### Paso 6: modificar el archivo local

```bash
cat > app.py << 'EOF'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"version": "2.0", "mensaje": "Cambio visto desde bind mount"})

@app.route("/nuevo")
def nuevo():
    return jsonify({"endpoint": "creado sin reconstruir imagen"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
EOF
```

### Paso 7: reiniciar servicio y validar

```bash
docker compose restart web
curl http://localhost:5001/
curl http://localhost:5001/nuevo
```

No se ejecutó `docker compose up --build` porque no fue necesario reconstruir la imagen. El archivo local está montado dentro del contenedor.

### Paso 8: limpiar

```bash
docker compose down
```

---

## Ejercicio 3: Healthcheck para PostgreSQL

### Objetivo

Agregar un healthcheck para distinguir entre un contenedor encendido y un servicio realmente listo.

Un contenedor puede estar en estado `running`, pero PostgreSQL todavía puede estar inicializando. El healthcheck ejecuta una prueba periódica para validar si el servicio acepta conexiones.

### Paso 1: crear carpeta del ejercicio

```bash
mkdir -p ejercicio03-healthcheck
cd ejercicio03-healthcheck
```

### Paso 2: crear docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: pitdb
      POSTGRES_USER: pituser
      POSTGRES_PASSWORD: pitpass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pituser -d pitdb"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s
EOF
```

`pg_isready` es una herramienta incluida en PostgreSQL para verificar si el servidor acepta conexiones. `interval` indica cada cuánto se ejecuta. `timeout` indica cuánto espera cada intento. `retries` indica cuántos fallos seguidos se toleran. `start_period` da un tiempo de gracia al inicio.

### Paso 3: levantar y observar estado

```bash
docker compose up -d
docker compose ps
```

Al inicio puede aparecer `starting`. Después de unos segundos debe aparecer `healthy`.

### Paso 4: ver detalle del healthcheck

```bash
docker inspect ejercicio03-healthcheck-db-1 --format='{{json .State.Health}}'
```

El inspect muestra los intentos del healthcheck, el código de salida y la salida del comando `pg_isready`.

### Paso 5: validar conexión

```bash
docker compose exec db pg_isready -U pituser -d pitdb
docker compose exec db psql -U pituser -d pitdb -c "SELECT 1;"
```

### Paso 6: limpiar

```bash
docker compose down
```

---

## Ejercicio 4: Backup y restauración de PostgreSQL

### Objetivo

Crear datos, exportarlos con `pg_dump`, eliminar la tabla y restaurar la información con `psql`.

Un volumen conserva datos localmente, pero un backup es una copia exportable. Si el volumen se borra o se corrompe, el backup permite recuperar información.

### Paso 1: crear carpeta del ejercicio

```bash
mkdir -p ejercicio04-backup-restore
cd ejercicio04-backup-restore
```

### Paso 2: crear docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: pitdb
      POSTGRES_USER: pituser
      POSTGRES_PASSWORD: pitpass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
EOF
```

### Paso 3: levantar base de datos

```bash
docker compose up -d
docker compose exec db pg_isready -U pituser -d pitdb
```

### Paso 4: crear tabla e insertar datos

```bash
docker compose exec db psql -U pituser -d pitdb -c \
  "CREATE TABLE tareas (id SERIAL PRIMARY KEY, titulo TEXT, estado TEXT);"

docker compose exec db psql -U pituser -d pitdb -c \
  "INSERT INTO tareas (titulo, estado) VALUES ('Preparar slides', 'hecho'), ('Practicar demo', 'pendiente'), ('Subir material', 'pendiente');"

docker compose exec db psql -U pituser -d pitdb -c \
  "SELECT * FROM tareas;"
```

### Paso 5: crear backup

```bash
mkdir -p backups

docker compose exec -T db pg_dump -U pituser pitdb > backups/pitdb.sql
```

El flag `-T` desactiva la terminal interactiva. Es importante cuando se redirige la salida con `>` hacia un archivo local.

### Paso 6: revisar archivo de backup

```bash
ls -lh backups
grep "CREATE TABLE" backups/pitdb.sql
grep "COPY public.tareas" backups/pitdb.sql
```

El archivo `pitdb.sql` contiene instrucciones para recrear estructura y datos.

### Paso 7: simular pérdida de información

```bash
docker compose exec db psql -U pituser -d pitdb -c "DROP TABLE tareas;"
docker compose exec db psql -U pituser -d pitdb -c "SELECT * FROM tareas;"
```

El `SELECT` debe fallar porque la tabla fue eliminada.

### Paso 8: restaurar backup

```bash
docker compose exec -T db psql -U pituser pitdb < backups/pitdb.sql
```

`psql` lee el archivo SQL y ejecuta sus instrucciones dentro de la base de datos.

### Paso 9: validar restauración

```bash
docker compose exec db psql -U pituser -d pitdb -c "SELECT * FROM tareas;"
```

Los datos deben volver a aparecer.

### Paso 10: limpiar

```bash
docker compose down -v
```

---

## Ejercicio 5: Flask + PostgreSQL con volumen, healthcheck y backup

### Objetivo

Levantar una app Flask y PostgreSQL usando Compose con volumen nombrado, healthcheck y backup.

### Paso 1: crear carpeta

```bash
mkdir -p ejercicio05-compose-postgres
cd ejercicio05-compose-postgres
```

### Paso 2: crear app.py

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

### Paso 3: crear requirements.txt

```bash
cat > requirements.txt << 'EOF'
Flask==3.0.3
psycopg2-binary==2.9.9
EOF
```

### Paso 4: crear Dockerfile

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

### Paso 5: crear compose.yaml

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

### Paso 6: levantar el proyecto

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

### Paso 7: probar la app

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

### Paso 8: ver datos directamente en PostgreSQL

```bash
docker compose exec db psql -U appuser -d appdb -c "SELECT * FROM visitas;"
```

### Paso 9: insertar tabla clientes

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

### Paso 10: backup con pg_dump

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

### Paso 11: probar persistencia del volumen

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

### Paso 12: borrar todo incluyendo volumen

Solo al final:

```bash
docker compose down -v
```

---

## Ejercicio 6: Nginx + Flask + PostgreSQL con volumen

### Objetivo

Crear una arquitectura más parecida a producción con Nginx como reverse proxy.

### Paso 1: crear carpeta

```bash
mkdir -p ejercicio06-nginx-proxy
cd ejercicio06-nginx-proxy
mkdir -p nginx
```

### Paso 2: crear app.py

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

### Paso 3: crear requirements.txt

```bash
cat > requirements.txt << 'EOF'
Flask==3.0.3
psycopg2-binary==2.9.9
gunicorn==22.0.0
EOF
```

### Paso 4: crear Dockerfile multi-stage

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

### Paso 5: crear configuración de Nginx

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

### Paso 6: crear compose.yaml

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

### Paso 7: levantar arquitectura

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

### Paso 8: probar desde el host

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

### Paso 9: comprobar que Flask no está publicado

```bash
curl http://localhost:5000
```

Debe fallar.

### Paso 10: ver volumen

```bash
docker volume ls
docker volume inspect ejercicio06-nginx-proxy_dbdata
```

El nombre real del volumen puede cambiar según la carpeta.

### Paso 11: apagar sin borrar volumen

```bash
docker compose down
```

### Paso 12: borrar incluyendo volumen

```bash
docker compose down -v
```

---

## Ejercicio 7: Laboratorio final — Mini Inventario

### Objetivo

Integrar lo aprendido en un proyecto completo desde cero.

La aplicación se llamará `Mini Inventario PIT`. Permitirá registrar items desde endpoints HTTP, guardarlos en PostgreSQL, conservar datos con volumen, verificar salud de la base de datos y crear un backup.

### Paso 1: crear carpeta del laboratorio final

```bash
mkdir -p ejercicio07-mini-inventario
cd ejercicio07-mini-inventario
```

### Paso 2: crear app.py

```bash
cat > app.py << 'EOF'
import os
import time
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "inventario"),
        user=os.getenv("DB_USER", "inventario_user"),
        password=os.getenv("DB_PASSWORD", "inventario_pass"),
        port=5432,
    )

def prepare_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    return jsonify({
        "proyecto": "Mini Inventario PIT",
        "db_host": os.getenv("DB_HOST", "db"),
        "rutas": [
            "/items",
            "/items/<categoria>/<nombre>",
            "/health"
        ]
    })

@app.route("/health")
def health():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as error:
        return jsonify({"status": "error", "detail": str(error)}), 500

@app.route("/items")
def list_items():
    prepare_db()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, categoria, nombre, creado_en FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({
        "total": len(rows),
        "items": [
            {"id": row[0], "categoria": row[1], "nombre": row[2], "creado_en": str(row[3])}
            for row in rows
        ]
    })

@app.route("/items/<categoria>/<nombre>")
def add_item(categoria, nombre):
    prepare_db()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (categoria, nombre) VALUES (%s, %s) RETURNING id",
        (categoria, nombre),
    )
    item_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": item_id, "categoria": categoria, "nombre": nombre})

if __name__ == "__main__":
    time.sleep(3)
    app.run(host="0.0.0.0", port=5000)
EOF
```

La ruta `/health` valida que Flask pueda conectarse a PostgreSQL. Las rutas `/items` y `/items/<categoria>/<nombre>` permiten listar y crear registros.

### Paso 3: crear requirements.txt

```bash
cat > requirements.txt << 'EOF'
flask==3.0.3
psycopg2-binary==2.9.9
EOF
```

### Paso 4: crear Dockerfile

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

### Paso 5: crear .env y .env.example

```bash
cat > .env << 'EOF'
DB_HOST=db
DB_NAME=inventario
DB_USER=inventario_user
DB_PASSWORD=inventario_pass
EOF

cat > .env.example << 'EOF'
DB_HOST=db
DB_NAME=
DB_USER=
DB_PASSWORD=
EOF
```

### Paso 6: crear docker-compose.yml completo

```bash
cat > docker-compose.yml << 'EOF'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s
    networks:
      - backend

volumes:
  postgres_data:

networks:
  backend:
EOF
```

El servicio `web` publica solo el puerto de Flask. El servicio `db` no publica `5432`, por lo tanto PostgreSQL queda interno. Ambos servicios pertenecen a la red `backend`. El volumen `postgres_data` conserva la información. El healthcheck permite saber cuándo PostgreSQL está listo.

`depends_on` con `condition: service_healthy` hace que `web` espere a que `db` pase el healthcheck antes de arrancar.

### Paso 7: levantar stack completo

```bash
docker compose up -d --build
docker compose ps
```

La columna de estado debe mostrar que `db` está `healthy`.

### Paso 8: probar aplicación

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/items
curl http://localhost:5000/items/redes/switch
curl http://localhost:5000/items/docker/compose
curl http://localhost:5000/items/postgres/volumen
curl http://localhost:5000/items
```

Los items se guardan en PostgreSQL. Si se recrea el contenedor, los datos se mantienen por el volumen.

### Paso 9: comprobar red y puertos

```bash
docker compose ps
docker network inspect ejercicio07-mini-inventario_backend
```

`web` debe mostrar `5000:5000`. `db` no debe publicar `5432`. En la red `backend` deben aparecer ambos contenedores.

### Paso 10: comprobar persistencia

```bash
docker compose down
docker compose up -d
curl http://localhost:5000/items
```

Los datos deben seguir existiendo.

### Paso 11: crear backup

```bash
mkdir -p backups
docker compose exec -T db pg_dump -U inventario_user inventario > backups/inventario.sql
ls -lh backups
```

### Paso 12: simular pérdida y restaurar

```bash
docker compose exec db psql -U inventario_user -d inventario -c "DROP TABLE items;"
curl http://localhost:5000/items

docker compose exec -T db psql -U inventario_user inventario < backups/inventario.sql
curl http://localhost:5000/items
```

Después de restaurar, los items deben volver.

### Paso 13: limpiar laboratorio final

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
| `down -v` borró datos | `-v` elimina volúmenes | Usarlo solo para reiniciar desde cero |
