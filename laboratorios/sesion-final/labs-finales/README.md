# Docker — Laboratorios Prácticos

> Guía completa: [GUIA.md](./GUIA.md)

Material práctico para la última sesión del curso Docker. Los 4 laboratorios cubren desde los comandos esenciales de la CLI hasta un stack de producción con healthchecks, backups, hardening y logging.

## Laboratorios

| Lab | Tema | Carpeta |
|-----|------|---------|
| 1 | Docker CLI, contenedores, volúmenes y redes | [`lab1/`](./lab1/README.md) |
| 2 | Dockerfile e imagen custom Flask | [`lab2/`](./lab2/README.md) |
| 3 | Docker Compose con Flask, PostgreSQL y Nginx | [`lab3/`](./lab3/README.md) |
| 4 | Producción: healthchecks, backups, límites y hardening | [`lab4/`](./lab4/README.md) |

## Uso rápido

```bash
# Lab 2 — Construir imagen
cd lab2
docker build -t gestor-tareas:v1.0 .

# Lab 3 — Levantar stack completo
cd ../lab3
cp .env.example .env
docker compose up -d --build

# Lab 4 — Stack de producción
cd ../lab4
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

No subas archivos `.env` reales al repositorio. Usa `.env.example` como plantilla.