# Laboratorio Sesion 4: Datos Persistentes Y Redes Internas

## Objetivo

Mejorar el stack Flask + PostgreSQL para que la base de datos sea interna, use volumen persistente, tenga healthcheck y pueda respaldarse.

## Archivos

Codigo base: [`../../codigo/sesion4`](../../codigo/sesion4/)

```text
codigo/sesion4/
  app.py
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
  .dockerignore
```

## Preparar Variables

```bash
cd codigo/sesion4
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## Levantar El Stack

```bash
docker compose up -d --build
docker compose ps
```

Probar la app:

```bash
curl http://localhost:5000
curl http://localhost:5000/add
curl http://localhost:5000
```

## Revisar Red Interna

```bash
docker network ls
docker network inspect <red>
docker compose exec web sh
```

Dentro del contenedor `web`, el host de la base de datos es `db`, no `localhost`.

## Revisar Volumen

```bash
docker volume ls
docker volume inspect <volumen>
```

Detener sin borrar datos:

```bash
docker compose down
docker compose up -d
```

Borrar datos persistentes:

```bash
docker compose down -v
```

## Crear Backup

```bash
mkdir backups
docker compose exec -T db pg_dump -U appuser appdb > backups/appdb.sql
```

En PowerShell:

```powershell
New-Item -ItemType Directory -Path backups -Force
docker compose exec -T db pg_dump -U appuser appdb > backups/appdb.sql
```

## Restaurar Backup

```bash
docker compose exec -T db psql -U appuser appdb < backups/appdb.sql
```

## Errores Frecuentes

| Error | Causa | Solucion |
|---|---|---|
| App no conecta a BD | Host incorrecto | Usar `DB_HOST=db` |
| BD expuesta al host | Se agrego `ports` en `db` | Quitar `ports` si no hace falta |
| Datos desaparecen | Falta volumen nombrado | Revisar `postgres_data` |
| Healthcheck no pasa | Usuario o base incorrectos | Revisar `.env` y `pg_isready` |
| Backup vacio o falla | Servicio `db` no esta listo | Revisar `docker compose ps` |
