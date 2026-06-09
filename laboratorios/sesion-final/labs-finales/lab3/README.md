# Lab 3 - Docker Compose Multi-servicio

Stack completo con Nginx, Flask y PostgreSQL.

## Ejecutar

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
curl http://localhost:8080
```

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

`docker compose down -v` elimina tambien el volumen de PostgreSQL.
