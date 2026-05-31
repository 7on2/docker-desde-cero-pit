# 🐳 Fundamentos de Docker — 5ta Sesión

## Repaso: Creación de Imágenes

### Aplicación Flask de ejemplo

```python
from flask import Flask

app = Flask(__name__)

@app.route('/hi')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 1. Dockerfile con imagen base Ubuntu

Convertimos la aplicación Flask a una imagen Docker usando **Ubuntu 24.04** como base:

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get clean all

# Usamos el flag para saltar la protección del sistema
RUN pip3 install flask --break-system-packages

ADD app.py /tmp/hello.py

EXPOSE 5000

CMD ["python3", "/tmp/hello.py"]
```

> Si existen varios Dockerfiles en el mismo directorio, los renombramos como `Dockerfile2`, `Dockerfile3`, etc.

---

## 2. Construir la imagen (`docker build`)

### Sintaxis general

```bash
docker build [OPCIONES] -t <repositorio>:<tag> <contexto>
```

### Parámetros relevantes

| Parámetro | Descripción |
|---|---|
| `-t` | Nombre y etiqueta de la imagen |
| `-f` | Especifica un Dockerfile distinto al predeterminado |
| `--no-cache` | Fuerza reconstrucción sin usar capas previas |
| `--pull` | Fuerza actualización de la imagen base |
| `--build-arg` | Pasa argumentos de construcción |
| `--platform` | Arquitectura objetivo (ej. `linux/amd64`, `linux/arm64`) |
| `--progress=plain` | Salida detallada del proceso |

### Ejemplo

```bash
docker build -f Dockerfile2 -t flask-hi:1.0 .
```

### Verificación

```bash
docker images
```

---

## 3. Ejecutar el contenedor (`docker run`)

### Sintaxis general

```bash
docker run [OPCIONES] <imagen>:<tag>
```

### Ejemplo con `-P`

```bash
docker run -d -P flask-hi:1.0
```

#### ¿Qué hace el flag `-P` (mayúscula)?

En lugar de elegir el puerto manualmente (como con `-p 5000:5000`), el flag `-P` le dice a Docker: **"Mira todos los puertos declarados en `EXPOSE` y conéctalos a puertos aleatorios de tu máquina"**.

```bash
docker ps
# Aquí verás el puerto aleatorio asignado
```

---

## 4. Optimización: imagen base de Python

En lugar de partir desde Ubuntu e instalar Python manualmente, usamos una imagen oficial de Python que ya viene lista:

```dockerfile
FROM python:3.12-slim

RUN pip install flask

ADD app.py /tmp/hello.py

EXPOSE 5000

CMD ["python", "/tmp/hello.py"]
```

> Esta imagen es considerablemente más liviana que la versión con Ubuntu.

---

## 5. Publicar la imagen en Docker Hub

Una vez construida la imagen optimizada, el siguiente paso es publicarla en **Docker Hub**.

### Paso 1 — Crear cuenta y repositorio

1. Regístrate en [hub.docker.com](https://hub.docker.com)
2. Crea un repositorio (ej: `flask-hi`)
3. Anota tu **username** (ej: `tuusuario`)

### Paso 2 — Login desde la terminal

```bash
docker login
```

> Si usas 2FA o token, genera un **Access Token** en:
> Docker Hub → Account Settings → Security → New Access Token

```bash
docker login -u tuusuario
# Pega tu token cuando pida contraseña
```

### Paso 3 — Taggear la imagen correctamente

Docker Hub exige el formato: `<tuusuario>/<repositorio>:<tag>`

```bash
# Construir directamente con el nombre correcto
docker build -f Dockerfile3 -t tuusuario/flask-hi:1.0 .

# O re-etiquetar una imagen existente
docker tag flask-hi:1.0 tuusuario/flask-hi:1.0
```

Verificar:

```bash
docker images
# Verás ambas: flask-hi:1.0  y  tuusuario/flask-hi:1.0
```

### Paso 4 — Publicar (push)

```bash
docker push tuusuario/flask-hi:1.0
```

> Docker subirá capa por capa. Las capas ya existentes en Hub se omiten automáticamente.

### Paso 5 — Verificar la publicación

```bash
# Eliminar la imagen local para forzar descarga real
docker rmi tuusuario/flask-hi:1.0

# Descargar desde Docker Hub
docker pull tuusuario/flask-hi:1.0

# Correr directo desde Hub (si no existe local, la descarga automáticamente)
docker run -d -P tuusuario/flask-hi:1.0
```

---

## 6. Buenas prácticas al publicar

Siempre taggea con versión específica **y** con `latest`:

```bash
docker tag tuusuario/flask-hi:1.0 tuusuario/flask-hi:latest
docker push tuusuario/flask-hi:latest
```

---

## Resumen del flujo completo

```
Código  →  Dockerfile  →  docker build  →  docker tag  →  docker push  →  Docker Hub
                                                                               ↓
                                                                          docker pull
                                                                      (cualquier máquina)
```

### Comandos útiles de referencia

| Comando | Para qué sirve |
|---|---|
| `docker images` | Ver imágenes locales |
| `docker ps` | Ver contenedores en ejecución |
| `docker push tuusuario/flask-hi:latest` | Publicar como `latest` |
| `docker pull tuusuario/flask-hi:1.0` | Descargar en otra máquina |
| `docker search flask` | Buscar imágenes en Hub desde terminal |
| `docker logout` | Cerrar sesión de Docker Hub |
