# Sesion 2: Dockerfile Profesional

## Objetivo

Crear imagenes propias con instrucciones clave, optimizarlas usando capas y cache, excluir archivos con `.dockerignore` y publicar imagenes con tags.

## Dockerfile

Un Dockerfile es la receta de una imagen. Docker lee sus instrucciones en orden y crea capas reutilizables.

| Instruccion | Para que sirve |
|---|---|
| `FROM` | Define la imagen base |
| `RUN` | Ejecuta comandos durante el build |
| `COPY` | Copia archivos al filesystem de la imagen |
| `WORKDIR` | Define el directorio de trabajo |
| `ENV` | Define variables de entorno |
| `EXPOSE` | Documenta puertos |
| `CMD` | Comando por defecto del contenedor |

## Capas y cache

Docker reutiliza capas si la instruccion y sus dependencias no cambiaron. Por eso conviene copiar primero archivos estables como `requirements.txt`, instalar dependencias y recien despues copiar el codigo de la app.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

## .dockerignore

Evita enviar archivos innecesarios o sensibles al contexto de build.

```text
__pycache__
*.pyc
.git
.env
node_modules
venv/
.venv/
```

## Imagenes base

- `python:3.12`: completa, mas pesada.
- `python:3.12-slim`: buena relacion tamano/compatibilidad.
- `python:3.12-alpine`: mas ligera, pero puede requerir ajustes por `musl`.

## Publicacion

```bash
docker login
docker tag mi-flask:v2 usuario/mi-flask:v2
docker push usuario/mi-flask:v2
```

---

[Anterior: Contenedores desde cero](./01-contenedores-desde-cero.md) | [Siguiente: Docker Compose](./03-docker-compose.md)
