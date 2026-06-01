# Sesion 4: Redes, Volumenes Y Persistencia

## Objetivo

Entender como los servicios se comunican dentro de Docker, como persistir datos y como proteger componentes internos como PostgreSQL.

## 1. Redes Docker

Cuando usas Docker Compose, cada proyecto recibe una red interna por defecto. Dentro de esa red, los contenedores se encuentran usando el nombre del servicio.

Ejemplo mental:

- `web` no se conecta a `localhost` para llegar a PostgreSQL.
- `web` se conecta al host `db`, porque `db` es el nombre del servicio en Compose.
- Solo publicamos puertos cuando necesitamos acceder desde el host o navegador.

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
```

En este caso, `web` esta publicado hacia el host, pero `db` puede permanecer interno.

## 2. Puerto Publicado Vs Comunicacion Interna

| Caso | Direccion correcta |
|---|---|
| Navegador hacia la app | `localhost:5000` |
| App hacia PostgreSQL | `db:5432` |
| Otro servicio interno hacia la app | `web:5000` |

Regla practica: si el usuario no necesita entrar directamente, no publiques el puerto.

## 3. Redes Explicitas

La red por defecto suele bastar para proyectos pequenos. Una red explicita ayuda cuando quieres documentar mejor la arquitectura o separar trafico.

```yaml
services:
  web:
    networks:
      - backend

  db:
    networks:
      - backend

networks:
  backend:
```

## 4. Volumenes

Un contenedor es reemplazable. Los datos importantes no deben depender del filesystem interno del contenedor.

Tipos comunes:

| Tipo | Uso recomendado |
|---|---|
| Volumen nombrado | Bases de datos y datos persistentes |
| Bind mount | Desarrollo local y edicion de codigo |
| Sin volumen | Pruebas descartables |

Ejemplo para PostgreSQL:

```yaml
services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 5. Servicios Internos

Bases de datos, colas, Redis y workers normalmente no deben exponerse al host. Deben estar disponibles solo dentro de la red Docker del proyecto.

```yaml
services:
  db:
    image: postgres:16
    # Sin ports: no se expone al host
```

## 6. Healthchecks

Un contenedor puede estar `running` pero todavia no estar listo. Un healthcheck declara como comprobar el estado real del servicio.

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## 7. Backup Y Restauracion

Un volumen conserva datos localmente, pero un backup crea una copia exportable.

Crear backup:

```bash
mkdir backups
docker compose exec -T db pg_dump -U appuser appdb > backups/appdb.sql
```

Restaurar:

```bash
docker compose exec -T db psql -U appuser appdb < backups/appdb.sql
```

## Comandos Utiles

```bash
docker network ls
docker network inspect <red>
docker volume ls
docker volume inspect <volumen>
docker compose ps
docker compose logs -f
docker compose down
docker compose down -v
```

## Cierre

Al final de esta sesion debes poder:

- Explicar la diferencia entre puerto publicado y comunicacion interna.
- Conectar servicios usando nombres de servicio.
- Persistir datos con volumenes nombrados.
- Mantener PostgreSQL como servicio interno.
- Validar estado con healthchecks.
- Crear y restaurar un backup basico.

---

[Anterior: Docker Compose](./03-docker-compose.md) | [Siguiente: Docker en produccion](./05-docker-en-produccion.md)
