# Docker - Laboratorios Finales

Material practico para la ultima sesion del curso Docker. Esta carpeta acompana al guion `../GuionFinal.md` y contiene los archivos listos para que los alumnos practiquen en clase.

## Laboratorios

| Lab | Tema | Carpeta |
|-----|------|---------|
| 1 | Docker CLI, contenedores, volumenes y redes | `lab1/` |
| 2 | Dockerfile e imagen custom Flask | `lab2/` |
| 3 | Docker Compose con Flask, PostgreSQL y Nginx | `lab3/` |
| 4 | Produccion: healthchecks, backups, limites y hardening | `lab4/` |

## Uso rapido

```bash
cd labs-finales/lab2
docker build -t gestor-tareas:v1.0 .

cd ../lab3
cp .env.example .env
docker compose up -d --build

cd ../lab4
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

No subas archivos `.env` reales al repositorio. Usa `.env.example` como plantilla.
