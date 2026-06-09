#!/bin/bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
FECHA="$(date +%Y%m%d-%H%M%S)"
CONTENEDOR="${CONTENEDOR:-tareas-db}"
DB_USER="${DB_USER:-admin}"
DB_NAME="${DB_NAME:-tareas_db}"
RETENTION_DIAS="${RETENTION_DIAS:-7}"

mkdir -p "$BACKUP_DIR"

STATUS="$(docker inspect "$CONTENEDOR" --format '{{.State.Health.Status}}' 2>/dev/null || true)"
if [ "$STATUS" != "healthy" ]; then
    echo "[ERROR] Contenedor $CONTENEDOR no esta healthy. Status: ${STATUS:-no encontrado}"
    exit 1
fi

docker exec "$CONTENEDOR" pg_dump -U "$DB_USER" -d "$DB_NAME" -F c > "$BACKUP_DIR/backup-${FECHA}.dump"
echo "[OK] Backup creado: $BACKUP_DIR/backup-${FECHA}.dump"

find "$BACKUP_DIR" -name '*.dump' -mtime +"$RETENTION_DIAS" -delete
echo "[OK] Backups antiguos eliminados. Retencion: $RETENTION_DIAS dias"
