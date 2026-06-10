# LAB 4 — Producción: Healthchecks, Backups y Seguridad

El laboratorio final integra todos los conceptos del curso y aplica prácticas de producción real: monitoreo de salud, backups automatizados de la base de datos, límites de recursos, seguridad de contenedores y registro de logs.

## Objetivo

- Implementar y verificar healthchecks completos.
- Automatizar backups de PostgreSQL con `docker exec` y `docker cp`.
- Aplicar límites de recursos (CPU y memoria).
- Endurecer la seguridad de los contenedores (`read-only`, capabilities, `no-new-privileges`).
- Configurar logging drivers y rotación de logs.
- Exportar e importar imágenes con `docker save` y `docker load`.

---

## Estructura del proyecto

```
lab4/
├── docker-compose.prod.yml ← stack completo de producción
├── backup.sh               ← script de backup automatizado
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── requirements.txt
├── app/
│   ├── app.py
│   └── templates/
│       └── index.html
├── nginx/
│   └── nginx.conf
└── db/
    └── init.sql
```

---

## Paso 1 — Healthchecks en Profundidad

### 1.1 Estados posibles de salud

| Estado | Descripción |
|--------|-------------|
| `starting` | Estado inicial. Docker aún no ha ejecutado el primer check (respeta `start_period`). |
| `healthy` | El check pasó exitosamente el número mínimo de veces. |
| `unhealthy` | El check falló `retries` veces consecutivas. Docker puede reiniciar el contenedor. |
| `none` | No hay `HEALTHCHECK` definido. El contenedor nunca reporta estado de salud. |

### 1.2 Healthcheck en `docker-compose.yml`

```yaml
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  app:
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:5000/ > /dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 1.3 Inspeccionar el estado de salud

```bash
docker compose ps
docker inspect tareas-db --format '{{json .State.Health}}' | python3 -m json.tool
docker inspect tareas-db --format '{{.State.Health.Status}}'
docker inspect tareas-app --format 'Status: {{.State.Health.Status}} | FailStreak: {{.State.Health.FailingStreak}}'
```

---

## Paso 2 — Backups de Base de Datos

### 2.1 Backup manual con `pg_dump`

```bash
mkdir -p ~/lab4/backups

docker exec tareas-db pg_dump \
  -U admin -d tareas_db -F c \
  > ~/lab4/backups/backup-$(date +%Y%m%d-%H%M%S).dump

ls -lh ~/lab4/backups/
```

### 2.2 Backup con `docker cp`

```bash
docker cp tareas-db:/etc/postgresql/postgresql.conf \
  ~/lab4/backups/postgresql.conf.bak 2>/dev/null || echo 'Archivo no encontrado'

docker compose stop db
docker run --rm \
  -v lab4_postgres-data:/data \
  -v ~/lab4/backups:/backup \
  alpine tar czf /backup/pgdata-$(date +%Y%m%d).tar.gz -C /data .
docker compose start db
```

### 2.3 Restaurar desde un backup

```bash
docker exec tareas-db createdb -U admin tareas_db_restored
BACKUP_FILE=~/lab4/backups/backup-20250120-143000.dump
docker cp $BACKUP_FILE tareas-db:/tmp/restore.dump
docker exec tareas-db pg_restore -U admin -d tareas_db_restored -F c /tmp/restore.dump
docker exec tareas-db psql -U admin -d tareas_db_restored -c 'SELECT count(*) FROM tareas;'
```

### 2.4 Script de backup automatizado (`backup.sh`)

El script ya está incluido en este directorio. Úsalo así:

```bash
chmod +x backup.sh
./backup.sh
ls -lh backups/
```

Para automatizar con cron:

```bash
crontab -e
# Agregar: 0 2 * * * /bin/bash ~/lab4/backup.sh
```

---

## Paso 3 — Límites de Recursos

### 3.1 Límites en `docker run`

```bash
docker run -d \
  --name app-limitada \
  --cpus 0.5 \
  --memory 256m \
  --memory-swap 256m \
  -p 5001:5000 \
  gestor-tareas:v1.0

docker inspect app-limitada --format 'CPU: {{.HostConfig.NanoCpus}} | Mem: {{.HostConfig.Memory}}'
docker stats app-limitada --no-stream
```

| Flag | Explicación |
|------|-------------|
| `--cpus 0.5` | 0.5 = 50% de 1 CPU. El contenedor no puede usar más de medio núcleo. |
| `--memory 256m` | Límite de RAM. Si lo supera, el proceso es killed (OOM). |
| `--memory-swap 256m` | Igual que `--memory` → deshabilita el swap. |

### 3.2 Límites en `docker-compose.yml`

```yaml
  app:
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  db:
    deploy:
      resources:
        limits:
          cpus: '1.00'
          memory: 512M
        reservations:
          cpus: '0.50'
          memory: 256M
```

---

## Paso 4 — Endurecimiento de Seguridad

### 4.1 Filesystem de solo lectura

```bash
docker run -d \
  --name app-ro \
  --read-only \
  --tmpfs /tmp \
  -v datos-app:/app/data \
  gestor-tareas:v1.0

docker exec app-ro touch /etc/hack 2>&1
# Debe devolver: touch: /etc/hack: Read-only file system
```

### 4.2 Linux Capabilities

```bash
docker run -d \
  --name app-caps \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  gestor-tareas:v1.0

docker run -d \
  --name app-secure \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --read-only \
  --tmpfs /tmp \
  gestor-tareas:v1.0
```

| Flag | Explicación |
|------|-------------|
| `--cap-drop ALL` | Elimina todas las capabilities. Nada de privilegios por defecto. |
| `--cap-add NET_BIND_SERVICE` | Agrega capacidad de escuchar en puertos < 1024. |
| `--security-opt no-new-privileges:true` | Bloquea escalada de privilegios via setuid/setgid. |
| `--read-only` | Filesystem root del contenedor es inmutable. |

### 4.3 Seguridad en `docker-compose.yml`

El archivo `docker-compose.prod.yml` de este laboratorio incluye:

- `security_opt: - no-new-privileges:true` en todos los servicios
- `cap_drop: - ALL` con solo las capabilities necesarias agregadas
- `read_only: true` y `tmpfs` para el servicio app
- Logging con rotación configurada

---

## Paso 5 — Logging y Rotación de Logs

### 5.1 Configurar el logging driver

```bash
docker inspect tareas-app --format '{{.HostConfig.LogConfig.Type}}'

docker run -d \
  --name app-logs \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  gestor-tareas:v1.0

docker inspect app-logs --format '{{.LogPath}}'
```

### 5.2 Logging en `docker-compose.yml`

```yaml
  app:
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'

  db:
    logging:
      driver: json-file
      options:
        max-size: '5m'
        max-file: '5'

  nginx:
    logging:
      driver: json-file
      options:
        max-size: '20m'
        max-file: '5'
```

---

## Paso 6 — Exportar e Importar Imágenes

### 6.1 Exportar imágenes con `docker save`

```bash
docker save -o gestor-tareas-v1.tar gestor-tareas:v1.0
ls -lh gestor-tareas-v1.tar

docker save gestor-tareas:v1.0 | gzip > gestor-tareas-v1.tar.gz
ls -lh gestor-tareas-v1.tar.gz

docker save -o stack-completo.tar \
  gestor-tareas:v1.0 \
  nginx:1.25-alpine \
  postgres:15-alpine
```

| Comando | Explicación |
|---------|-------------|
| `docker save` | Exporta una o más imágenes con **todas sus capas** y metadatos. Restaurable con `docker load`. |
| `docker export` | Exporta el filesystem de un contenedor como snapshot plano (sin capas). |
| `gzip` | Compresión estándar. Reduce el `.tar` considerablemente. |

### 6.2 Importar imágenes con `docker load`

```bash
docker load -i gestor-tareas-v1.tar
docker load < gestor-tareas-v1.tar.gz
docker images | grep gestor-tareas
docker run -d --name app-importada -p 5002:5000 gestor-tareas:v1.0
```

---

## Paso 7 — Ejecutar Stack de Producción

```bash
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
curl http://localhost:8080/health
```

## Inspeccionar

```bash
docker inspect tareas-db --format '{{.State.Health.Status}}'
docker stats --no-stream
docker logs tareas-nginx --tail 20
```

## Backup

```bash
chmod +x backup.sh
./backup.sh
ls -lh backups/
```

## Limpieza

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml down -v
```

---

## Paso 8 — Checklist de Despliegue en Producción

Antes de llevar un stack Docker a producción, verifica estos puntos:

1. Healthchecks definidos en todos los servicios críticos.
2. Restart policy configurada (`unless-stopped` o `on-failure`).
3. Variables sensibles en archivo `.env`, nunca hardcodeadas.
4. `.env` en `.gitignore` y `.dockerignore`.
5. Límites de CPU y memoria establecidos para cada servicio.
6. Usuario no-root definido en el Dockerfile (`USER appuser`).
7. `--security-opt no-new-privileges:true` en todos los servicios.
8. `cap_drop: ALL` + solo las capabilities necesarias agregadas.
9. Logging driver configurado con rotación (`max-size`, `max-file`).
10. Backups automatizados con script y política de retención.
11. Imágenes exportadas con `docker save` para disaster recovery.
12. Redes segmentadas: servicios no expuestos directamente al exterior.

---

## Resumen del Laboratorio 4

| Concepto / Comando | Función |
|--------------------|---------|
| `HEALTHCHECK` (Dockerfile y Compose) | Monitoreo de salud: `starting` → `healthy` / `unhealthy`. |
| `docker exec + pg_dump` | Backup de PostgreSQL ejecutando herramienta nativa dentro del contenedor. |
| `docker cp` | Backup de archivos individuales del contenedor al host. |
| `--cpus / --memory / deploy.resources` | Límites de recursos para garantizar estabilidad del host. |
| `--cap-drop ALL + --cap-add` | Mínimo privilegio: eliminar capabilities innecesarias. |
| `--security-opt no-new-privileges` | Bloquear escalada de privilegios desde dentro del contenedor. |
| `--read-only + tmpfs` | Filesystem inmutable excepto directorios explícitamente permitidos. |
| Logging driver + `max-size` | Evitar que los logs llenen el disco del host. |
| `docker save / docker load` | Transportar imágenes sin registry. Disaster recovery offline. |