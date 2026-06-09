# Lab 2 - Dockerfile e Imagen Custom

Construye una imagen propia para una aplicacion Flask.

> Para ejecutarla necesitas una base PostgreSQL accesible y las variables `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`. En clase se completa con el Lab 3.

```bash
docker build -t gestor-tareas:v1.0 .
docker history gestor-tareas:v1.0
docker build -f Dockerfile.multistage -t gestor-tareas:slim .
```
