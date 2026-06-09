# Lab 4 - Produccion y Operacion

Practica final con healthchecks, backups, limites de recursos, hardening y logging.

## Ejecutar stack de produccion

```bash
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
curl http://localhost:8080/health
```

## Backup

```bash
chmod +x backup.sh
./backup.sh
ls -lh backups/
```

## Inspeccion

```bash
docker inspect tareas-db --format '{{.State.Health.Status}}'
docker stats --no-stream
docker logs tareas-nginx --tail 20
```

## Exportar imagen para disaster recovery

```bash
docker save gestor-tareas:v1.0 -o gestor-tareas-v1.0.tar
docker load -i gestor-tareas-v1.0.tar
```

## Limpieza

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml down -v
```
