# Sesion 2: Dockerfile, Imagenes y Docker Hub

## Objetivo

Crear imagenes propias desde una app Flask, entender cada instruccion del Dockerfile, comprender el sistema de capas y cache, optimizar builds con `.dockerignore`, comparar imagenes base, versionar con tags y publicar en Docker Hub.

## Flujo principal

```text
Dockerfile  ->  imagen  ->  contenedor
receta      ->  molde   ->  proceso ejecutandose
```

## 1. Versionamiento de imagenes

Versionar una imagen significa darle un nombre y un tag:

```text
mi-flask:v1
mi-flask:v2
mi-flask:prod
mi-flask:2026-01
```

### Ejemplo: app Flask versionada

```bash
mkdir flask-versionado
cd flask-versionado
```

Archivos base en [`../../codigo/sesion2/`](../../codigo/sesion2/):

```bash
docker build -t mi-flask:v1 .
docker run -d --name flask-v1 -p 5000:5000 mi-flask:v1
curl http://localhost:5000
docker stop flask-v1
docker rm flask-v1
```

## 2. Instrucciones del Dockerfile

| Instruccion | Para que sirve |
|---|---|
| `FROM` | Define la imagen base |
| `WORKDIR` | Define el directorio de trabajo dentro de la imagen |
| `COPY` | Copia archivos desde la maquina local a la imagen |
| `RUN` | Ejecuta comandos durante la construccion de la imagen |
| `EXPOSE` | Documenta que puerto usa la aplicacion |
| `CMD` | Comando por defecto cuando arranca el contenedor |

### FROM

```text
FROM ubuntu       -> tengo Linux base
FROM python       -> tengo Linux + Python
FROM node         -> tengo Linux + Node.js
```

### WORKDIR

Sin `WORKDIR`:
```dockerfile
COPY app.py /app/app.py
CMD ["python", "/app/app.py"]
```

Con `WORKDIR`:
```dockerfile
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

### COPY

```dockerfile
COPY requirements.txt .
```

El punto final significa la carpeta actual dentro de la imagen (`/app` porque antes pusimos `WORKDIR /app`).

### RUN

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

```text
RUN se ejecuta cuando construyo la imagen.
CMD se ejecuta cuando arranco el contenedor.
```

`--no-cache-dir` evita guardar cache innecesario de pip y reduce el tamano de la imagen.

### EXPOSE

```dockerfile
EXPOSE 5000
```

`EXPOSE` documenta el puerto pero no lo publica. Para publicar usamos `-p`:

```bash
docker run -p 5000:5000 mi-flask:v1
```

```text
5000 de mi maquina -> 5000 del contenedor
```

### CMD

Forma recomendada (exec form):
```dockerfile
CMD ["python", "app.py"]
```

Evitar para produccion (shell form):
```dockerfile
CMD python app.py
```

La forma con lista maneja mejor senales del sistema y argumentos.

## 3. Capas y cache

Una imagen Docker es una pila de capas:

```text
Imagen mi-flask:v1
┌─────────────────────────────────┐
│ COPY app.py .                    │ capa 5
├─────────────────────────────────┤
│ RUN pip install ...              │ capa 4
├─────────────────────────────────┤
│ COPY requirements.txt .          │ capa 3
├─────────────────────────────────┤
│ WORKDIR /app                     │ capa 2
├─────────────────────────────────┤
│ FROM python:3.12-slim            │ capa base
└─────────────────────────────────┘
```

Ver capas:
```bash
docker history mi-flask:v1
```

### Demostracion de cache

```bash
# Primera construccion
docker build -t mi-flask:v1 .

# Segunda construccion (mas rapida por cache)
docker build -t mi-flask:v1 .
```

Si solo cambia `app.py`, Docker reutiliza la capa de `pip install`:

```bash
docker build -t mi-flask:v2 .
```

### Capa escribible del contenedor

```text
Contenedor ejecutandose
┌─────────────────────────────────┐
│ Capa escribible del contenedor   │ aqui cambian archivos en runtime
├─────────────────────────────────┤
│ COPY app.py .                    │ solo lectura
├─────────────────────────────────┤
│ RUN pip install ...              │ solo lectura
├─────────────────────────────────┤
│ FROM python:3.12-slim            │ solo lectura
└─────────────────────────────────┘
```

Ejercicio:
```bash
docker run -it --name prueba-escritura mi-flask:v1 sh
echo "archivo creado dentro del contenedor" > temporal.txt
ls
exit

docker rm prueba-escritura

docker run -it --name prueba-escritura-2 mi-flask:v1 sh
ls
# temporal.txt no aparece
exit

docker rm prueba-escritura-2
```

## 4. Multistage build

Usar varias etapas dentro del mismo Dockerfile. La primera etapa construye o prepara algo, la segunda copia solo lo necesario para ejecutar.

```text
Etapa 1 = cocina: hay herramientas, ollas, ingredientes, desorden
Etapa 2 = plato final: solo se entrega lo necesario
```

### Dockerfile.multistage

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN python -m venv /venv
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /venv /venv
COPY app.py .

ENV PATH="/venv/bin:$PATH"
EXPOSE 5000
CMD ["python", "app.py"]
```

Linea clave:
```dockerfile
COPY --from=builder /venv /venv
```

Construir:
```bash
docker build -f Dockerfile.multistage -t mi-flask:multi .
```

### Ejercicio comparativo

```bash
# Construir con Dockerfile normal
docker build -t mi-flask:v2 .

# Construir con multistage
docker build -f Dockerfile.multistage -t mi-flask:multi .

# Comparar tamanos
docker images | grep mi-flask
docker history mi-flask:v2
docker history mi-flask:multi
```

## 5. .dockerignore

El contexto de build es la carpeta que Docker envia al construir. `.dockerignore` le dice a Docker que archivos ignorar.

### Comparacion con Git

| Archivo | Herramienta | Que evita |
|---|---|---|
| `.gitignore` | Git | Que archivos entren al repositorio |
| `.dockerignore` | Docker | Que archivos entren al contexto de build |

### Contenido recomendado

```text
__pycache__
*.pyc
.git
.env
venv/
.venv/
*.log
Dockerfile.*
README.md
```

### Patrones comunes

| Patron | Motivo |
|---|---|
| `__pycache__` | Cache local de Python |
| `*.pyc` | Archivos compilados localmente |
| `.git` | Historial del repo, innecesario en la imagen |
| `.env` | Puede contener secretos |
| `venv/` | Entorno virtual local, pesado e innecesario |
| `*.log` | Logs locales no deben entrar a la imagen |

## 6. Imagenes base: slim vs alpine

| Imagen | Ventaja | Cuidado |
|---|---|---|
| `python:3.12` | Completa, compatible | Pesa mas |
| `python:3.12-slim` | Buen equilibrio | Puede requerir paquetes extra |
| `python:3.12-alpine` | Muy pequena | Puede complicar dependencias nativas |

### Ejercicio comparativo

```bash
docker build -f Dockerfile.slim -t flask:slim .
docker build -f Dockerfile.alpine -t flask:alpine .
docker images | grep flask
```

`slim` es la recomendacion segura para empezar. `alpine` es util pero hay que saber manejar sus diferencias con `musl`.

## 7. Docker Hub

Docker Hub es un registro de imagenes.

```text
GitHub guarda repositorios de codigo.
Docker Hub guarda imagenes Docker.
```

Flujo:
```text
Mi computadora -> docker push -> Docker Hub
Otra computadora -> docker pull -> descarga la imagen
```

Ejemplos de imagenes publicas:
```bash
docker pull nginx
docker pull postgres:16
docker pull python:3.12-slim
```

## 8. Etiquetado de imagenes

Formato:
```text
usuario/repositorio:tag
```

| Parte | Significado |
|---|---|
| `anthg` | Usuario o namespace en Docker Hub |
| `mi-flask` | Nombre del repositorio de imagen |
| `v1` | Version o etiqueta |

Comando:
```bash
docker tag mi-flask:v1 tuusuario/mi-flask:v1
```

`docker tag` no reconstruye la imagen, solo le agrega otro nombre.

### Versionamiento

```bash
docker build -t mi-flask:v1 .
docker tag mi-flask:v1 tuusuario/mi-flask:v1

docker build -t mi-flask:v2 .
docker tag mi-flask:v2 tuusuario/mi-flask:v2
```

Evitar depender siempre de `latest`. `latest` no significa la mejor version, solo es un tag mas.

## 9. Push y pull

### Push

```bash
docker login
docker tag mi-flask:v1 tuusuario/mi-flask:v1
docker push tuusuario/mi-flask:v1
```

### Pull

```bash
docker pull tuusuario/mi-flask:v1
docker run -d --name flask-remoto -p 5000:5000 tuusuario/mi-flask:v1
curl http://localhost:5000
docker stop flask-remoto
docker rm flask-remoto
```

### Resumen de comandos

```text
build = construir imagen
tag   = nombrar/versionar imagen
push  = subir imagen
pull  = descargar imagen
run   = crear contenedor desde imagen
```

## 10. Variables de entorno utiles

| Variable | Para que sirve |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1` | Evita crear archivos `.pyc` |
| `PYTHONUNBUFFERED=1` | Muestra logs de Python sin retraso |

## 11. Errores frecuentes

| Error | Causa probable | Solucion |
|---|---|---|
| `port is already allocated` | Ya hay otro contenedor usando el puerto | Cambiar puerto o detener el contenedor anterior |
| `COPY failed` | El archivo no existe o estas en otra carpeta | Revisar `pwd`, `ls` y nombre del archivo |
| `ModuleNotFoundError: flask` | No se instalo `requirements.txt` | Revisar `RUN pip install...` |
| `denied: requested access` | Imagen mal etiquetada o sin login | Usar `docker login` y `tuusuario/repositorio:tag` |
| La imagen pesa mucho | Se copiaron archivos innecesarios | Revisar `.dockerignore` |
| Cambios no aparecen | Se esta ejecutando una imagen vieja | Reconstruir con nuevo tag y recrear contenedor |

## 12. Comandos resumen

```bash
# Construir
docker build -t flask-final:v1 .

# Ver imagenes
docker images

# Ver capas
docker history flask-final:v1

# Ejecutar
docker run -d --name flask-final -p 5000:5000 flask-final:v1

# Probar
curl http://localhost:5000

# Etiquetar
docker tag flask-final:v1 tuusuario/flask-final:v1

# Login
docker login

# Subir
docker push tuusuario/flask-final:v1

# Descargar
docker pull tuusuario/flask-final:v1

# Limpiar
docker stop flask-final
docker rm flask-final
```

---

[Anterior: Contenedores desde cero](./01-contenedores-desde-cero.md) | [Siguiente: Docker Compose](./03-docker-compose.md)
