# Sesion 3: Docker Compose Y Aplicaciones Multi-Contenedor

## Objetivo

Levantar proyectos con varios servicios, entender `docker-compose.yml`, integrar Flask con PostgreSQL y configurar variables con `.env`.

## Por que Compose

Una aplicacion real no vive sola: puede necesitar base de datos, proxy, cache o workers. Ejecutar todo con `docker run` se vuelve repetitivo. Compose permite describir el stack completo en YAML.

```mermaid
flowchart LR
    A["compose.yml"] --> B["docker compose"] --> C["web + db + red + volumen"]
    style A fill:#1f6feb,stroke:#58a6ff,color:#fff
    style B fill:#8957e5,stroke:#bc8cff,color:#fff
    style C fill:#238636,stroke:#3fb950,color:#fff
```

## Estructura base

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
```

## Flask + PostgreSQL

Dentro de Compose, `localhost` apunta al contenedor actual. Para conectar Flask a PostgreSQL se usa el nombre del servicio: `db`.

```text
Navegador -> localhost:5000 -> servicio web -> db:5432 -> PostgreSQL
```

## Variables con .env

```text
DB_HOST=db
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=appsecret
FLASK_ENV=development
```

No subas `.env` con secretos reales a GitHub. Usa `.env.example` para documentar las variables requeridas.

## Comandos esenciales

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
docker compose exec web sh
docker compose down
```

---

[Anterior: Dockerfile profesional](./02-dockerfile-profesional.md) | [Siguiente: Redes, volumenes y persistencia](./04-redes-volumenes-persistencia.md)
