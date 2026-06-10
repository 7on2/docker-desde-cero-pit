# LAB 3 — Docker Compose: Orquestación Multi-servicio

En este laboratorio levantaremos un stack completo con Flask, PostgreSQL y Nginx usando un solo archivo `docker-compose.yml`.

## Objetivo

- Entender la estructura de un archivo `docker-compose.yml`.
- Configurar redes segmentadas (frontend/backend) para aislar servicios.
- Usar healthchecks y `depends_on` para controlar el orden de inicio.
- Dominar los comandos esenciales de Docker Compose.

---

## Estructura del proyecto

```
lab3/
├── docker-compose.yml     ← definición de todo el stack
├── .env.example           ← variables de entorno (plantilla)
├── .env                   ← copia local con valores reales (NO subir a git)
├── .gitignore
├── .dockerignore
├── Dockerfile             ← imagen de Flask (reutilizado del Lab 2)
├── requirements.txt
├── app/
│   ├── app.py
│   └── templates/
│       └── index.html
├── nginx/
│   └── nginx.conf         ← configuración del reverse proxy
└── db/
    └── init.sql           ← SQL de inicialización de la BD
```

---

## Paso 1 — Preparar entorno

```bash
cp .env.example .env
# Edita .env con tus valores si lo deseas (los defaults funcionan)
```

---

## Paso 2 — Archivos de Soporte

### 2.1 Archivo `.env`

Centraliza las configuraciones sensibles fuera del código:

```env
POSTGRES_DB=tareas_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=SuperSecreta123!
FLASK_ENV=production
SECRET_KEY=cambiarEnProduccion_abc123xyz
NGINX_PORT=80
```

> **WARN:** Agrega `.env` a tu `.gitignore`. Los secretos **NUNCA** deben estar en el repositorio.

### 2.2 Script de inicialización de la base de datos (`db/init.sql`)

```sql
CREATE TABLE IF NOT EXISTS tareas (
    id         SERIAL PRIMARY KEY,
    titulo     VARCHAR(255) NOT NULL,
    completado BOOLEAN DEFAULT FALSE,
    creado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tareas (titulo) VALUES
    ('Revisar configuración de Wazuh'),
    ('Actualizar reglas de ModSecurity'),
    ('Documentar arquitectura SOC');
```

### 2.3 Configuración de Nginx (`nginx/nginx.conf`)

Nginx actúa como proxy inverso: recibe peticiones HTTP en el puerto 80 y las redirige a Flask en el puerto 5000.

```nginx
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        client_max_body_size 10M;

        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;

        location / {
            proxy_pass http://app:5000;
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## Paso 3 — El archivo `docker-compose.yml`

El stack define 3 servicios:

- **db**: PostgreSQL con healthcheck y volumen persistente
- **app**: Flask construida desde Dockerfile con healthcheck
- **nginx**: Reverse proxy con configuración montada como read-only

Dos redes segmentadas:
- `backend`: app ↔ db
- `frontend`: nginx ↔ app

La base de datos **nunca** queda expuesta directamente al exterior.

---

## Paso 4 — Comandos Esenciales de Docker Compose

### 4.1 Levantar el stack

```bash
cd ~/lab3

docker compose up -d
docker compose up -d --build
docker compose up -d db app
docker compose ps
docker compose logs
docker compose logs -f
docker compose logs -f app
docker compose logs --tail 50 db
```

### 4.2 Operar servicios individuales

```bash
docker compose exec db psql -U admin -d tareas_db
# Dentro de psql: \dt para listar tablas, SELECT * FROM tareas;

docker compose exec app bash
docker compose restart nginx
docker compose top
```

### 4.3 Detener y limpiar

```bash
docker compose stop
docker compose start
docker compose down
docker compose down -v
docker compose down --rmi local
docker compose down -v --rmi all
```

| Comando | Explicación |
|---------|-------------|
| `docker compose up -d` | Levanta el stack completo en background. |
| `docker compose down` | Limpia el stack. Sin `-v` conserva los datos en volúmenes. |
| `docker compose exec svc cmd` | Como `docker exec` pero por nombre de servicio. |
| `docker compose logs -f svc` | Streaming de logs de un servicio específico. |
| `docker compose ps` | Estado resumido: nombre, imagen, estado, puertos. |

---

## Paso 5 — Verificar el Stack

```bash
docker compose ps
# Todos deben mostrar: Up (healthy)

curl http://localhost:8080

curl -X POST http://localhost:8080/tareas \
     -H 'Content-Type: application/json' \
     -d '{"titulo": "Tarea desde Lab 3"}'

docker compose exec db psql -U admin -d tareas_db -c 'SELECT * FROM tareas;'

docker inspect tareas-db --format '{{.State.Health.Status}}'
docker inspect tareas-app --format '{{.State.Health.Status}}'

docker network ls | grep lab3
docker network inspect lab3_backend
```

---

## Probar API

```bash
curl -X POST http://localhost:8080/tareas \
  -H 'Content-Type: application/json' \
  -d '{"titulo":"Practicar docker compose"}'
```

## Apagar

```bash
docker compose down
docker compose down -v
```

`docker compose down -v` elimina también el volumen de PostgreSQL.

---

## Resumen del Laboratorio 3

| Concepto | Función |
|----------|---------|
| `version / services / networks / volumes` | Cuatro bloques principales del `docker-compose.yml`. |
| `image:` vs `build:` | Usar imagen pre-existente vs construir desde Dockerfile. |
| `environment:` con `.env` | Separar configuración del código. Variables nunca hardcodeadas. |
| `depends_on: condition: service_healthy` | Orden de inicio correcto basado en healthchecks. |
| Redes `frontend` / `backend` | Segmentación: nginx no puede acceder a `db` directamente. |
| Volúmenes nombrados | Persistencia de datos independiente del ciclo del contenedor. |
| `docker compose up/down/logs/exec` | Comandos esenciales del ciclo de vida de un stack Compose. |