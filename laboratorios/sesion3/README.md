# Laboratorio Sesion 3: Flask + PostgreSQL Con Docker Compose

## Objetivo

Levantar una aplicacion Flask y una base de datos PostgreSQL con un solo archivo `docker-compose.yml`.

## Archivos

Codigo base: [`../../codigo/sesion3`](../../codigo/sesion3/)

```text
codigo/sesion3/
  app.py
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
```

## Preparar Variables

```bash
cd codigo/sesion3
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
docker compose logs -f
```

Probar:

```bash
curl http://localhost:5000
```

## Entrar A Un Servicio

```bash
docker compose exec web sh
```

## Detener

```bash
docker compose down
```

Para borrar tambien el volumen de PostgreSQL:

```bash
docker compose down -v
```

## Errores Frecuentes

| Error | Causa | Solucion |
|---|---|---|
| Flask no conecta a PostgreSQL | Usas `localhost` como host | Usar `DB_HOST=db` |
| Variables vacias | No existe `.env` | Copiar `.env.example` a `.env` |
| Puerto ocupado | Otro proceso usa 5000 | Cambiar a `5001:5000` |
| Datos se pierden | No hay volumen | Usar volumen nombrado |
