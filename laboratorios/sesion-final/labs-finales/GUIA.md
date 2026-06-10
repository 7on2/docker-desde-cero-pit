# Docker — Laboratorios Prácticos
## Clase Final · OTI-UNI · Instructor: Tony

---

> **Estructura del documento**
> | Lab | Tema |
> |-----|------|
> | LAB 1 | Fundamentos: Docker CLI desde Cero |
> | LAB 2 | Dockerfile y Construcción de Imágenes Custom |
> | LAB 3 | Docker Compose: Orquestación Multi-servicio |
> | LAB 4 | Producción: Healthchecks, Backups y Seguridad |

---

# LABORATORIO 1 — Fundamentos: Docker CLI desde Cero

En este laboratorio recorreremos los comandos esenciales de Docker: gestión de imágenes, contenedores, redes, volúmenes y transferencia de archivos. Todo se ejecuta directamente desde la terminal, sin escribir aún ningún Dockerfile ni Compose.

## Objetivo

- Comprender el ciclo de vida completo de un contenedor.
- Dominar `docker run`, `docker ps`, `docker exec`, `docker cp`.
- Gestionar imágenes locales: `pull`, `tag`, `rmi`, `inspect`.
- Crear y usar redes y volúmenes desde la CLI.

---

## Conceptos Clave (recordatorio rápido)

| Término           | Descripción                                                                        |
| ----------------- | ---------------------------------------------------------------------------------- |
| **Imagen**        | Plantilla de solo lectura. Es el "molde" del contenedor. Ej: `nginx:latest`        |
| **Contenedor**    | Instancia en ejecución de una imagen. Tiene su propio filesystem, red y proceso.   |
| **Docker Daemon** | Proceso que corre en background y gestiona todo. Se llama `dockerd`.               |
| **Registry**      | Repositorio de imágenes. El público por defecto es Docker Hub (`hub.docker.com`).  |
| **Layer**         | Capa del sistema de archivos. Las imágenes se construyen por capas apiladas.       |
| **Volume**        | Directorio persistente gestionado por Docker, sobrevive al borrado del contenedor. |
| **Bind Mount**    | Monta una carpeta real del host dentro del contenedor. Muy útil en desarrollo.     |
| **Network**       | Red virtual que conecta contenedores entre sí de forma aislada.                    |

---

## Paso 1 — Gestión de Imágenes

### 1.1 Descargar una imagen con `docker pull`

`docker pull` descarga la imagen desde Docker Hub al sistema local. La imagen queda guardada en caché para usarla sin conexión.

```bash
# Descargar la imagen oficial de nginx (web server ligero)
docker pull nginx

# Descargar una versión específica (tag)
docker pull nginx:1.25-alpine

# Descargar imagen de ubuntu versión 22.04
docker pull ubuntu:22.04
```

| Comando | Explicación |
|---------|-------------|
| `docker pull nginx` | Descarga `nginx:latest` (el tag `latest` se asume si no se especifica) |
| `docker pull nginx:1.25-alpine` | Descarga la versión exacta 1.25 basada en Alpine Linux (~8MB vs ~50MB) |
| `:alpine` | Variante mínima. Alpine Linux es una distro de ~5MB ideal para producción. |

---

### 1.2 Listar y explorar imágenes locales

```bash
# Listar todas las imágenes descargadas
docker images

# Alias equivalente
docker image ls

# Ver información detallada de una imagen (JSON completo)
docker image inspect nginx

# Ver solo campos específicos con --format (Go template)
docker image inspect nginx --format '{{.Config.ExposedPorts}}'
```

| Comando | Explicación |
|---------|-------------|
| `docker images` | Lista: `REPOSITORY`, `TAG`, `IMAGE ID`, `CREATED`, `SIZE` |
| `docker image inspect nginx` | Devuelve JSON con: capas, variables de entorno, CMD, EXPOSE, autor, etc. |
| `--format '{{.Campo}}'` | Filtra la salida usando plantillas Go. Útil en scripts. |

---

### 1.3 Etiquetar y eliminar imágenes

```bash
# Crear un tag alternativo para la imagen
# Útil antes de subir tu propia imagen a un registry
docker tag nginx:latest mi-nginx:v1.0

# Listar para confirmar el nuevo tag
docker images | grep mi-nginx

# Eliminar una imagen por nombre:tag
docker rmi mi-nginx:v1.0

# Eliminar imagen solo si no hay contenedores usándola
# El flag -f fuerza la eliminación aunque haya dependencias
docker rmi -f nginx:1.25-alpine
```

| Comando | Explicación |
|---------|-------------|
| `docker tag <src> <dest>` | No copia datos: crea un puntero (alias) a la misma imagen subyacente. |
| `docker rmi` | *Remove Image*. Solo elimina el tag; la imagen real se borra cuando no quedan tags. |
| `-f / --force` | Fuerza la eliminación aunque la imagen esté en uso por un contenedor parado. |

---

## Paso 2 — Ciclo de Vida de Contenedores

### 2.1 Ejecutar el primer contenedor: `docker run`

`docker run` = `docker create` + `docker start`. Es el comando principal para lanzar contenedores.

```bash
# El clásico Hello World de Docker
docker run hello-world

# Ejecutar nginx y publicarlo en el puerto 8080 del host
# -d  → detached (corre en background, no bloquea la terminal)
# -p  → port mapping: <host_port>:<container_port>
# --name → nombre personalizado para el contenedor
docker run -d -p 8080:80 --name mi-web nginx

# Verificar que está corriendo
curl http://localhost:8080

# Ejecutar ubuntu de forma interactiva y entrar a la shell
# -i  → stdin interactivo (mantiene abierto el input)
# -t  → asigna pseudo-terminal (TTY)
docker run -it ubuntu:22.04 bash
# Dentro del contenedor puedes ejecutar: ls, apt update, etc.
# Para salir: exit  (el contenedor se detiene)

# Ejecutar un comando puntual sin quedarse dentro
docker run --rm ubuntu:22.04 echo 'Hola desde contenedor'
# --rm → elimina el contenedor automáticamente al terminar
```

| Flag | Explicación |
|------|-------------|
| `-d` | *Detached mode*. El contenedor corre en segundo plano y devuelve el ID. |
| `-p 8080:80` | Mapeo de puertos. El puerto 80 del contenedor queda accesible en el 8080 del host. |
| `--name` | Nombre legible. Sin esto Docker asigna nombres aleatorios como `pensive_euler`. |
| `-it` | `-i` + `-t` combinados. Necesario para shells interactivas como `bash` o `sh`. |
| `--rm` | *Auto-remove*. Limpio para contenedores temporales: no deja basura en `docker ps -a`. |

---

### 2.2 Gestionar contenedores en ejecución

```bash
# Ver contenedores activos
docker ps

# Ver TODOS (activos + detenidos)
docker ps -a

# Ver solo los IDs (útil para scripts)
docker ps -q

# Detener un contenedor (envía señal SIGTERM, espera 10s, luego SIGKILL)
docker stop mi-web

# Iniciar un contenedor detenido
docker start mi-web

# Reiniciar (stop + start)
docker restart mi-web

# Matar inmediatamente (SIGKILL, sin tiempo de gracia)
docker kill mi-web

# Eliminar un contenedor detenido
docker rm mi-web

# Eliminar un contenedor aunque esté corriendo
docker rm -f mi-web
```

| Comando | Explicación |
|---------|-------------|
| `docker ps` | Lista: `CONTAINER ID`, `IMAGE`, `COMMAND`, `CREATED`, `STATUS`, `PORTS`, `NAMES`. |
| `docker stop` | *Graceful shutdown*. Da tiempo al proceso para cerrar conexiones y liberar recursos. |
| `docker kill` | Brutal. Sin tiempo de gracia. Útil si `stop` tarda demasiado. |
| `docker rm` | Elimina el contenedor del registro. No elimina su imagen ni sus volúmenes nombrados. |

---

### 2.3 Interactuar con contenedores: `exec`, `logs`, `inspect`

```bash
# Volver a levantar nginx si lo borramos
docker run -d -p 8080:80 --name mi-web nginx

# Ejecutar un comando DENTRO de un contenedor ya corriendo
docker exec mi-web ls /etc/nginx

# Entrar a la shell del contenedor en ejecución
docker exec -it mi-web bash
# Dentro puedes explorar: cat /etc/nginx/nginx.conf
# Salir con: exit  (el contenedor SIGUE corriendo, no se detiene)

# Ver los logs del contenedor
docker logs mi-web

# Seguir los logs en tiempo real (como tail -f)
docker logs -f mi-web

# Ver solo las últimas 20 líneas
docker logs --tail 20 mi-web

# Inspeccionar configuración completa del contenedor (JSON)
docker inspect mi-web

# Ver solo la IP asignada
docker inspect mi-web --format '{{.NetworkSettings.IPAddress}}'

# Ver estadísticas de CPU y memoria en tiempo real
docker stats mi-web
```

| Comando | Explicación |
|---------|-------------|
| `docker exec -it <name> bash` | Abre shell en contenedor activo. Diferencia clave con `run`: no crea uno nuevo. |
| `docker logs -f` | *Follow mode*. Muy útil para debugging de apps sin entrar al contenedor. |
| `docker inspect` | JSON completo: red, volúmenes, variables de entorno, restart policy, etc. |
| `docker stats` | CPU %, Mem Usage/Limit, Net I/O, Block I/O. Actualiza en tiempo real. |

---

## Paso 3 — Transferencia de Archivos con `docker cp`

`docker cp` copia archivos entre el host y un contenedor sin necesidad de volúmenes. Es ideal para inspección y debugging rápido.

```bash
# Asegurarse de tener mi-web corriendo
docker ps | grep mi-web

# COPIAR del host AL contenedor
# Crear un archivo HTML personalizado en el host
echo '<h1>Docker Labs - UNI</h1>' > index.html

# Copiarlo a la ruta donde nginx sirve archivos
docker cp index.html mi-web:/usr/share/nginx/html/index.html

# Verificar que el cambio se aplicó
curl http://localhost:8080

# COPIAR del contenedor AL host
# Extraer el archivo de configuración de nginx del contenedor
docker cp mi-web:/etc/nginx/nginx.conf ./nginx-backup.conf

# Verificar la copia local
cat nginx-backup.conf

# También se puede copiar directorios completos
docker cp mi-web:/usr/share/nginx/html ./html-backup/
ls ./html-backup/
```

| Sintaxis | Explicación |
|----------|-------------|
| `docker cp <src> <dest>` | Funciona con contenedores detenidos también. No necesita que estén activos. |
| `host:ruta → nombre:/ruta` | Sintaxis: origen → destino. El nombre puede ser ID o nombre del contenedor. |
| `docker cp contenedor:/ruta ./local` | Extrae archivos del contenedor al directorio actual del host. |

---

## Paso 4 — Volúmenes y Persistencia

### 4.1 Tipos de almacenamiento en Docker

Sin volúmenes, todo lo que escribas dentro de un contenedor se pierde al borrarlo. Docker ofrece 3 formas de persistir datos:

| Tipo | Descripción |
|------|-------------|
| **Volume (nombrado)** | Docker gestiona la ubicación (`/var/lib/docker/volumes/`). Recomendado para bases de datos y producción. |
| **Bind Mount** | Carpeta del host montada en el contenedor. Ideal en desarrollo para editar código en tiempo real. |
| **tmpfs** | Solo en Linux. Almacena en RAM. Datos NO persisten ni siquiera si el contenedor vive. Para datos sensibles temporales. |

---

### 4.2 Crear y usar volumes nombrados

```bash
# Crear un volumen nombrado
docker volume create datos-nginx

# Listar volúmenes
docker volume ls

# Inspeccionar el volumen (ver su mountpoint en el host)
docker volume inspect datos-nginx

# Usar el volumen al crear un contenedor
# -v <volumen_nombrado>:<ruta_en_contenedor>
docker run -d \
  --name web-persistente \
  -p 8081:80 \
  -v datos-nginx:/usr/share/nginx/html \
  nginx

# Escribir contenido en el volumen a través del contenedor
docker exec web-persistente bash -c \
  "echo '<h1>Persistente!</h1>' > /usr/share/nginx/html/index.html"

# Borrar el contenedor
docker rm -f web-persistente

# Crear NUEVO contenedor usando el MISMO volumen → los datos persisten
docker run -d --name web-nuevo -p 8082:80 \
  -v datos-nginx:/usr/share/nginx/html nginx

curl http://localhost:8082   # Muestra 'Persistente!' aunque el contenedor es nuevo

# Eliminar un volumen (solo si no está en uso)
docker volume rm datos-nginx

# Eliminar todos los volúmenes sin uso
docker volume prune
```

---

### 4.3 Bind Mount en desarrollo

```bash
# Crear carpeta de trabajo en el host
mkdir -p ~/lab1/html
echo '<h1>Lab Docker - Bind Mount</h1>' > ~/lab1/html/index.html

# Montar la carpeta del host en el contenedor
# -v <ruta_absoluta_host>:<ruta_contenedor>
docker run -d \
  --name web-dev \
  -p 8083:80 \
  -v ~/lab1/html:/usr/share/nginx/html \
  nginx

# Editar el archivo en el HOST (no en el contenedor)
echo '<h1>Cambio en tiempo real!</h1>' > ~/lab1/html/index.html

# El cambio se refleja INMEDIATAMENTE sin reiniciar el contenedor
curl http://localhost:8083
```

> **TIP:** El bind mount es el método preferido durante el desarrollo. Al guardar código en tu editor de texto en el host, el contenedor lo ve al instante.

---

## Paso 5 — Redes en Docker

### 5.1 Redes por defecto

| Tipo | Descripción |
|------|-------------|
| `bridge` | Red por defecto. Cada contenedor obtiene una IP privada. El host accede con `-p`. Contenedores en la misma bridge custom pueden comunicarse por nombre. |
| `host` | El contenedor comparte la red del host directamente. Sin aislamiento de red. Solo Linux. |
| `none` | Sin red. El contenedor está completamente aislado de la red. |

---

### 5.2 Crear y usar redes custom

```bash
# Ver redes existentes
docker network ls

# Crear una red bridge personalizada
docker network create --driver bridge red-lab

# Inspeccionar la red (ver subnet, gateway)
docker network inspect red-lab

# Lanzar dos contenedores en la misma red
docker run -d --name servidor --network red-lab nginx
docker run -d --name cliente  --network red-lab alpine sleep 3600

# Desde 'cliente' hacer ping a 'servidor' por NOMBRE (DNS automático)
docker exec cliente ping -c 3 servidor
# En redes bridge custom, Docker actúa como DNS:
# 'servidor' resuelve automáticamente a la IP del contenedor 'servidor'

# Conectar un contenedor existente a una red adicional
docker network connect red-lab mi-web

# Desconectar de una red
docker network disconnect red-lab mi-web

# Eliminar red (solo si no hay contenedores conectados)
docker network rm red-lab
```

> **NOTA:** En la red bridge por defecto **NO** funciona resolución DNS por nombre. En redes custom **SÍ**. Por eso siempre se recomienda crear redes propias.

---

## Paso 6 — Limpieza del Sistema

```bash
# Ver cuánto espacio usa Docker
docker system df

# Eliminar contenedores detenidos
docker container prune

# Eliminar imágenes sin tag ('dangling images')
docker image prune

# Eliminar TODO lo que no esté en uso:
# contenedores, redes, imágenes colgantes, caché de build
docker system prune

# Versión agresiva: elimina también imágenes aunque tengan tag
docker system prune -a

# Incluir también los volúmenes (¡CUIDADO: borra datos!)
docker system prune -a --volumes
```

> **WARN:** `docker system prune -a --volumes` borra datos persistentes. Nunca en producción sin backup previo.

---

## Resumen del Laboratorio 1

| Comando | Función |
|---------|---------|
| `docker pull / images / rmi` | Descargar, listar y eliminar imágenes locales. |
| `docker run -d -p --name -it --rm` | Crear y ejecutar contenedores con diversas opciones. |
| `docker ps / stop / start / rm` | Gestionar el ciclo de vida de contenedores. |
| `docker exec / logs / stats` | Operar e inspeccionar contenedores en ejecución. |
| `docker cp` | Transferir archivos entre host y contenedor. |
| `docker volume create / -v` | Crear y montar volúmenes para persistencia. |
| `docker network create` | Crear redes para comunicación entre contenedores. |
| `docker system prune` | Limpiar recursos no utilizados. |

---

---

# LABORATORIO 2 — Dockerfile y Construcción de Imágenes Custom

En este laboratorio construiremos nuestra propia imagen Docker usando Dockerfile. Reutilizamos la aplicación de gestión de tareas (Flask + PostgreSQL + Nginx) del curso para que el contexto sea familiar.

## Objetivo

- Entender todas las instrucciones del Dockerfile y cuándo usarlas.
- Construir una imagen con `docker build` y optimizarla con multi-stage builds.
- Usar variables de entorno, `ARG` y `ENV` correctamente.
- Entender el sistema de capas y cómo el caché acelera los builds.

---

## Referencia: Instrucciones del Dockerfile

| Instrucción | Descripción |
|-------------|-------------|
| `FROM` | Define la imagen base. Siempre es la primera instrucción. Ej: `FROM python:3.11-slim` |
| `RUN` | Ejecuta un comando en tiempo de **BUILD**. Genera una nueva capa. Ej: `RUN apt-get install -y curl` |
| `COPY` | Copia archivos del host al filesystem de la imagen. Preferido sobre `ADD` para archivos locales. |
| `ADD` | Como `COPY` pero además puede descomprimir `.tar` y descargar URLs. Usar solo cuando se necesite. |
| `WORKDIR` | Establece el directorio de trabajo para instrucciones siguientes (`RUN`, `COPY`, `CMD`, `ENTRYPOINT`). |
| `ENV` | Variable de entorno disponible en **BUILD** y en **RUNTIME** (cuando el contenedor corre). |
| `ARG` | Variable solo en **BUILD**. No existe en tiempo de ejecución. Útil para versiones o tokens de CI. |
| `EXPOSE` | Documenta qué puerto escucha la app. No abre el puerto por sí solo. Es informativo. |
| `CMD` | Comando por defecto al iniciar el contenedor. Se puede sobreescribir con: `docker run <img> otro-cmd` |
| `ENTRYPOINT` | Comando principal del contenedor. No se sobreescribe fácilmente. `CMD` actúa como sus argumentos. |
| `VOLUME` | Marca un directorio como punto de montaje de volumen. Docker crea un volumen anónimo automáticamente. |
| `USER` | Cambia el usuario para instrucciones siguientes y para el proceso principal. Seguridad: evitar root. |
| `LABEL` | Agrega metadatos como clave=valor. Ej: `LABEL maintainer='tony@uni.edu.pe'` |
| `HEALTHCHECK` | Define cómo Docker comprueba si el contenedor está sano. Cambia `STATUS` a `healthy` o `unhealthy`. |

---

## Paso 1 — Estructura del Proyecto

Crearemos la siguiente estructura de directorios para la app de gestión de tareas:

```bash
mkdir -p ~/lab2/app
cd ~/lab2

# La estructura final será:
# lab2/
# ├── Dockerfile          ← imagen de la app Flask
# ├── .dockerignore       ← archivos a excluir del contexto
# ├── requirements.txt    ← dependencias Python
# └── app/
#     ├── app.py          ← código de la aplicación Flask
#     └── templates/
#         └── index.html  ← plantilla HTML
```

---

### 1.1 Archivo `requirements.txt`

Lista las librerías Python que necesita la aplicación:

```text
# ~/lab2/requirements.txt
Flask==3.0.3
psycopg2-binary==2.9.9
python-dotenv==1.0.1
gunicorn==22.0.0
```

| Librería | Rol |
|----------|-----|
| `Flask` | Framework web. Nuestro servidor HTTP. |
| `psycopg2-binary` | Driver para conectarse a PostgreSQL desde Python. |
| `python-dotenv` | Carga variables de entorno desde un archivo `.env`. |
| `gunicorn` | Servidor WSGI de producción para Flask (reemplaza al server de desarrollo). |

---

### 1.2 Código de la app (`app.py`)

No explicamos el código Python línea por línea (no es el objetivo del curso), pero sí su estructura general:

```python
# ~/lab2/app/app.py
# API REST con Flask que se conecta a PostgreSQL
# Endpoints:
#   GET  /            → lista todas las tareas
#   POST /tareas      → crea una tarea nueva
#   DELETE /tareas/<id> → elimina una tarea

import os
from flask import Flask, jsonify, request, render_template
import psycopg2

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        port=os.environ.get('DB_PORT', '5432')
    )

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, titulo, completado FROM tareas ORDER BY id')
    tareas = cur.fetchall()
    conn.close()
    return render_template('index.html', tareas=tareas)

@app.route('/tareas', methods=['POST'])
def crear_tarea():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO tareas (titulo) VALUES (%s)', (data['titulo'],))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## Paso 2 — Escribir el Dockerfile

### 2.1 Versión completa comentada línea por línea

```dockerfile
# ~/lab2/Dockerfile

# ── INSTRUCCIÓN FROM ──────────────────────────────────────────────────────────
# Imagen base: Python 3.11 en variante 'slim' (Debian mínimo)
# 'slim' = sin herramientas de compilación, más liviana que la imagen full
FROM python:3.11-slim

# ── INSTRUCCIÓN LABEL ─────────────────────────────────────────────────────────
# Metadatos informativos. No afectan el comportamiento.
# Se ven con: docker image inspect <imagen>
LABEL maintainer="tony@uni.edu.pe"
LABEL description="Gestor de Tareas - Docker Labs UNI"
LABEL version="1.0"

# ── INSTRUCCIÓN ARG ───────────────────────────────────────────────────────────
# Variable solo disponible durante el BUILD.
# Se puede sobreescribir al construir con:
#   docker build --build-arg APP_PORT=8000 .
ARG APP_PORT=5000

# ── INSTRUCCIÓN ENV ───────────────────────────────────────────────────────────
# Variable de entorno disponible en RUNTIME también.
# PYTHONDONTWRITEBYTECODE=1 → no genera archivos .pyc
# PYTHONUNBUFFERED=1        → output directo a stdout (para docker logs)
# PORT=${APP_PORT}          → toma el valor del ARG definido arriba
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=${APP_PORT}

# ── INSTRUCCIÓN WORKDIR ───────────────────────────────────────────────────────
# Establece /app como directorio de trabajo.
# Si no existe, Docker lo crea automáticamente.
# Todos los COPY, RUN, CMD siguientes son relativos a /app
WORKDIR /app

# ── INSTRUCCIÓN COPY (dependencies first) ────────────────────────────────────
# PRIMERO copiamos solo requirements.txt (no el código fuente).
# Razón: aprovechar el CACHE de Docker.
# Si el código cambia pero requirements.txt no, esta capa se reutiliza.
# Sin esto, cada cambio de código reinstalaría TODAS las dependencias.
COPY requirements.txt .

# ── INSTRUCCIÓN RUN ───────────────────────────────────────────────────────────
# Instalar dependencias Python.
# --no-cache-dir: no guarda caché de pip dentro de la imagen (ahorra espacio)
# --upgrade pip:  asegura versión reciente del gestor de paquetes
# El backslash \ permite partir el comando en varias líneas (más legible)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── INSTRUCCIÓN COPY (código fuente) ─────────────────────────────────────────
# Ahora sí copiamos TODO el código de la app.
# Se copia DESPUÉS de instalar deps para no invalidar el caché de pip
# con cada cambio de código.
# . (punto) = directorio actual del host → . (punto) = WORKDIR del contenedor
COPY app/ .

# ── INSTRUCCIÓN USER ──────────────────────────────────────────────────────────
# Crear usuario no-root y cambiar a él.
# Buena práctica de seguridad: nunca correr la app como root.
# --no-create-home: no crear directorio /home/appuser (innecesario)
# --shell /bin/false: el usuario no puede iniciar una shell (seguridad)
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

# ── INSTRUCCIÓN EXPOSE ────────────────────────────────────────────────────────
# Documentar que la app escucha en el puerto 5000.
# NO abre el puerto. Sirve de documentación y para herramientas
# como docker-compose que pueden usarlo automáticamente.
EXPOSE 5000

# ── INSTRUCCIÓN HEALTHCHECK ───────────────────────────────────────────────────
# Docker verificará la salud del contenedor periódicamente.
# --interval:     tiempo entre cada check
# --timeout:      tiempo máximo para que el check responda
# --start-period: tiempo de gracia al arrancar (la app puede tardar en iniciar)
# --retries:      intentos fallidos antes de marcar como 'unhealthy'
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" \
    || exit 1

# ── INSTRUCCIÓN CMD ───────────────────────────────────────────────────────────
# Comando por defecto al iniciar el contenedor.
# Usamos gunicorn (servidor de producción) en vez del server de desarrollo Flask.
# -w 2:              2 workers (procesos paralelos)
# -b 0.0.0.0:5000:   escuchar en todas las interfaces en el puerto 5000
# app:app →          módulo:objeto_Flask
# Formato JSON (exec form): evita que el proceso sea hijo de /bin/sh
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

---

### 2.2 Archivo `.dockerignore`

Equivalente al `.gitignore`. Excluye archivos del contexto de build para que no se copien a la imagen ni se envíen al daemon:

```gitignore
# ~/lab2/.dockerignore

# Control de versiones
__pycache__/
*.pyc
*.pyo
.git/
.gitignore

# Entornos virtuales Python (no deben ir en la imagen)
venv/
.venv/
env/

# Archivos de secretos (NUNCA incluir en una imagen)
.env
*.key
*.pem

# Documentación y tests (no necesarios en producción)
docs/
tests/
README.md

# Archivos del editor
.vscode/
.idea/
```

| Entrada | Razón |
|---------|-------|
| `.dockerignore` | Reduce el tamaño del contexto enviado al daemon y evita incluir secretos. |
| `__pycache__/ y *.pyc` | Archivos compilados de Python. Innecesarios y específicos del OS host. |
| `.env` | Archivo de variables de entorno. **NUNCA** debe quedar embebido en una imagen. |

---

## Paso 3 — Construir la imagen con `docker build`

```bash
# Ubicarse en el directorio del proyecto
cd ~/lab2

# Construir la imagen
# -t nombre:tag → nombre y etiqueta de la imagen
# .             → contexto de build: directorio actual
docker build -t gestor-tareas:v1.0 .

# Construir sin usar el caché (fuerza reinstalación de todo)
docker build --no-cache -t gestor-tareas:v1.0 .

# Construir pasando un ARG personalizado
docker build --build-arg APP_PORT=8000 -t gestor-tareas:v1.1 .

# Verificar que la imagen fue creada
docker images | grep gestor-tareas

# Ver el historial de capas (cada instrucción = una capa)
docker history gestor-tareas:v1.0

# Ver tamaño detallado de la imagen
docker image inspect gestor-tareas:v1.0 --format '{{.Size}}'
```

| Opción | Explicación |
|--------|-------------|
| `docker build -t <name>:<tag> .` | El punto es el **BUILD CONTEXT**: directorio desde donde Docker lee los archivos. |
| `--no-cache` | Fuerza reconstrucción de todas las capas. Útil para obtener dependencias nuevas. |
| `--build-arg CLAVE=valor` | Sobreescribe una variable `ARG` definida en el Dockerfile. |
| `docker history <image>` | Muestra cada capa: tamaño, instrucción. Sirve para detectar capas pesadas. |

---

## Paso 4 — Entendiendo el Sistema de Caché

El caché de Docker es uno de los conceptos más importantes para builds rápidos. Cada instrucción genera una capa. Si la instrucción y su contexto no cambian, Docker reutiliza la capa cacheada.

```bash
# Demostración del caché:

# Primera vez → construye todo (sin caché disponible)
docker build -t gestor-tareas:cache-test .

# Modificar SOLO el archivo app.py (simula un cambio de código)
echo '# comentario' >> app/app.py

# Segunda vez → Docker reutiliza hasta el COPY requirements.txt
# y el RUN pip install (capas 1-6 del caché)
# Solo reconstruye desde el COPY app/ en adelante
docker build -t gestor-tareas:cache-test .

# OBSERVAR en la salida:
# Cada línea que dice 'CACHED' = capa reutilizada del caché
# Solo las líneas sin 'CACHED' se ejecutaron de nuevo
```

> **TIP:** El orden de instrucciones importa para el caché. Siempre copia lo que cambia **menos** primero (`requirements.txt`) y lo que cambia **más** al final (código fuente). Esto minimiza los rebuilds.

---

## Paso 5 — Multi-Stage Build (Optimización)

Un multi-stage build usa múltiples `FROM` en el mismo Dockerfile. Las etapas anteriores se usan para compilar/construir, y solo la última se convierte en la imagen final. El resultado es una imagen mucho más pequeña.

```dockerfile
# ~/lab2/Dockerfile.multistage

# ═══ STAGE 1: builder ════════════════════════════════════════════════════════
# Etapa de construcción. Tiene pip y herramientas de compilación.
# Esta imagen NO será la imagen final.
FROM python:3.11 AS builder

WORKDIR /build

COPY requirements.txt .

# Instalar dependencias en una carpeta específica (/install)
# --target: instala las dependencias en un directorio especificado,
#           sin contaminar el Python del sistema.
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# ═══ STAGE 2: runtime ════════════════════════════════════════════════════════
# Imagen final de producción. Solo tiene lo necesario para CORRER la app.
# Sin pip, sin compiladores, sin código fuente del stage anterior.
FROM python:3.11-slim AS runtime

LABEL maintainer="tony@uni.edu.pe"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps

WORKDIR /app

# COPY --from=builder: copia SOLO las dependencias instaladas del stage 'builder'.
# No copia pip ni herramientas de compilación.
COPY --from=builder /install ./deps

# Copiar el código de la aplicación
COPY app/ .

RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" \
    || exit 1

CMD ["python", "-m", "gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
# Construir con el Dockerfile de multi-stage
docker build -f Dockerfile.multistage -t gestor-tareas:slim .

# Comparar tamaños
docker images | grep gestor-tareas
# gestor-tareas:v1.0  → ~200MB
# gestor-tareas:slim  → ~120MB  (ahorro significativo)
```

| Instrucción | Explicación |
|-------------|-------------|
| `FROM ... AS nombre` | Nombra una etapa para referenciarla después con `--from`. |
| `COPY --from=builder /src /dst` | Copia archivos **entre stages**. Permite separar build de runtime. |
| `-f Dockerfile.multistage` | Especifica qué Dockerfile usar cuando no se llama `Dockerfile`. |

---

## Resumen del Laboratorio 2

| Instrucción / Comando | Función |
|-----------------------|---------|
| `FROM / LABEL / ARG / ENV` | Base, metadatos y variables del Dockerfile. |
| `WORKDIR / COPY / ADD` | Configurar el filesystem de la imagen. |
| `RUN` | Ejecutar comandos durante el build (instalar, compilar, configurar). |
| `USER / EXPOSE / HEALTHCHECK` | Seguridad, documentación y monitoreo de salud. |
| `CMD / ENTRYPOINT` | Definir qué ejecuta el contenedor al iniciarse. |
| `docker build -t` | Construir una imagen desde un Dockerfile. |
| Multi-stage builds | Optimizar el tamaño de la imagen final separando build de runtime. |
| `.dockerignore` | Excluir archivos innecesarios o sensibles del contexto de build. |

---

---

# LABORATORIO 3 — Docker Compose: Orquestación Multi-servicio

Levantaremos el stack completo de la aplicación de gestión de tareas: Flask + PostgreSQL + Nginx como reverse proxy. Todo definido en un único archivo `docker-compose.yml`.

## Objetivo

- Entender la estructura y sintaxis de `docker-compose.yml`.
- Orquestar múltiples contenedores con dependencias entre ellos.
- Configurar redes, volúmenes y variables de entorno en Compose.
- Dominar los comandos esenciales de Docker Compose.

---

## Conceptos Clave de Docker Compose

| Concepto | Descripción |
|----------|-------------|
| `docker-compose.yml` | Archivo declarativo que define todos los servicios, redes y volúmenes del stack. |
| `service` | Un servicio = un contenedor (o conjunto de réplicas). Equivale a un `docker run` con opciones. |
| `depends_on` | Establece orden de inicio. El servicio A no inicia hasta que B esté `healthy` o `started`. |
| Redes en Compose | Cada servicio en la misma red puede hablar con otro usando su **nombre de servicio** como hostname. |
| Volúmenes en Compose | Volúmenes nombrados definidos a nivel de stack, reutilizables entre servicios. |
| `environment` | Variables de entorno inyectadas en el contenedor. Pueden venir de un archivo `.env`. |
| `profiles` | Permite tener servicios opcionales que solo se levantan con `--profile <nombre>`. |

---

## Paso 1 — Estructura del Proyecto

```bash
mkdir -p ~/lab3/{app/templates,nginx,db}
cd ~/lab3

# Estructura final:
# lab3/
# ├── docker-compose.yml     ← definición de todo el stack
# ├── .env                   ← variables de entorno (secretos)
# ├── Dockerfile             ← imagen de Flask (reutilizado del Lab 2)
# ├── requirements.txt
# ├── app/
# │   ├── app.py
# │   └── templates/
# │       └── index.html
# ├── nginx/
# │   └── nginx.conf         ← configuración del reverse proxy
# └── db/
#     └── init.sql           ← SQL de inicialización de la BD
```

---

## Paso 2 — Archivos de Soporte

### 2.1 Archivo `.env` (variables de entorno)

Centraliza las configuraciones sensibles fuera del código y del `docker-compose.yml`:

```env
# ~/lab3/.env
# Este archivo NUNCA debe subirse a git (.gitignore)

# Configuración de PostgreSQL
POSTGRES_DB=tareas_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=SuperSecreta123!

# Configuración de la App
FLASK_ENV=production
SECRET_KEY=cambiarEnProduccion_abc123xyz

# Puerto expuesto al host
NGINX_PORT=80
```

> **WARN:** Agrega `.env` a tu `.gitignore`. Los secretos (passwords, API keys) **NUNCA** deben estar en el repositorio de código.

---

### 2.2 Script de inicialización de la base de datos

```sql
-- ~/lab3/db/init.sql
-- Este script crea la tabla y agrega datos de ejemplo.
-- PostgreSQL lo ejecuta automáticamente si lo montamos en
-- /docker-entrypoint-initdb.d/  (punto de entrada oficial de la imagen postgres)

CREATE TABLE IF NOT EXISTS tareas (
    id         SERIAL PRIMARY KEY,
    titulo     VARCHAR(255) NOT NULL,
    completado BOOLEAN DEFAULT FALSE,
    creado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos de ejemplo
INSERT INTO tareas (titulo) VALUES
    ('Revisar configuración de Wazuh'),
    ('Actualizar reglas de ModSecurity'),
    ('Documentar arquitectura SOC');
```

---

### 2.3 Configuración de Nginx (reverse proxy)

Nginx actúa como proxy inverso: recibe peticiones HTTP en el puerto 80 y las redirige al contenedor Flask en el puerto 5000. El usuario nunca habla directamente con Flask:

```nginx
# ~/lab3/nginx/nginx.conf

# worker_processes: número de procesos worker de Nginx.
# 'auto' detecta el número de CPUs disponibles.
worker_processes auto;

events {
    # Máximo de conexiones simultáneas por worker.
    worker_connections 1024;
}

http {
    server {
        # Escuchar en el puerto 80 (HTTP)
        listen 80;

        # Aumentar el tamaño máximo de cuerpo en peticiones (uploads)
        client_max_body_size 10M;

        # Cabeceras de seguridad básicas
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;

        # Todas las peticiones a / se redirigen a Flask
        location / {
            # 'app' es el NOMBRE DEL SERVICIO en docker-compose.yml.
            # Docker Compose actúa como DNS: 'app' resuelve a la IP del contenedor Flask.
            proxy_pass http://app:5000;

            # Cabeceras que informan a Flask sobre el cliente original
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## Paso 3 — El archivo `docker-compose.yml`

Este es el corazón del laboratorio. Cada sección está explicada en detalle:

```yaml
# ~/lab3/docker-compose.yml

# La versión del esquema de Compose. '3.9' es la más reciente estable.
# Define qué características están disponibles.
version: '3.9'

# ── SERVICIOS ──────────────────────────────────────────────────────────────────
# Cada clave bajo 'services:' es un contenedor que Compose gestiona.
services:

  # ── SERVICIO: db (PostgreSQL) ──────────────────────────────────────────────
  db:
    # Imagen oficial de PostgreSQL versión 15.
    # 'alpine' al final = variante ligera basada en Alpine Linux.
    image: postgres:15-alpine

    # Nombre explícito del contenedor. Sin esto Compose genera 'lab3-db-1'.
    container_name: tareas-db

    # Política de reinicio automático:
    # unless-stopped = siempre reiniciar EXCEPTO si se paró manualmente.
    # Opciones: no | always | on-failure | unless-stopped
    restart: unless-stopped

    # Variables de entorno. Con ${VAR} lee del archivo .env automáticamente.
    environment:
      POSTGRES_DB:       ${POSTGRES_DB}
      POSTGRES_USER:     ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

    volumes:
      # Volumen nombrado para persistir los datos de PostgreSQL.
      # Si borramos el contenedor, los datos siguen en 'postgres-data'.
      - postgres-data:/var/lib/postgresql/data

      # Bind mount del script de inicialización.
      # PostgreSQL ejecuta automáticamente todos los .sql en este directorio
      # SOLO en el primer arranque (cuando el volumen está vacío).
      # ':ro' = read-only. El contenedor solo puede leer, no escribir.
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

    # Redes a las que pertenece este servicio.
    # 'db' solo está en la red interna, no expuesta al exterior.
    networks:
      - backend

    # Healthcheck: verifica que PostgreSQL esté listo para aceptar conexiones.
    # 'pg_isready' es la herramienta oficial de PostgreSQL para esto.
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s     # verificar cada 10 segundos
      timeout: 5s       # tiempo máximo de espera para el check
      retries: 5        # 5 fallos consecutivos → 'unhealthy'
      start_period: 20s # esperar 20s antes del primer check (tiempo de inicio)

  # ── SERVICIO: app (Flask) ──────────────────────────────────────────────────
  app:
    # En lugar de 'image:', usamos 'build:' para construir desde Dockerfile.
    # 'context' es el directorio donde está el Dockerfile.
    build:
      context: .           # directorio actual como contexto de build
      dockerfile: Dockerfile

    container_name: tareas-app
    restart: unless-stopped

    # Variables que necesita Flask para conectarse a la DB.
    # Nota: 'DB_HOST: db' → 'db' es el nombre del servicio PostgreSQL.
    # Compose hace de DNS: el contenedor 'app' puede hacer ping a 'db'.
    environment:
      DB_HOST:    db
      DB_NAME:    ${POSTGRES_DB}
      DB_USER:    ${POSTGRES_USER}
      DB_PASS:    ${POSTGRES_PASSWORD}
      FLASK_ENV:  ${FLASK_ENV}
      SECRET_KEY: ${SECRET_KEY}

    # depends_on + condition: service_healthy:
    # Flask NO iniciará hasta que PostgreSQL esté 'healthy'.
    # Esto evita que Flask arranque y falle porque la DB no está lista.
    depends_on:
      db:
        condition: service_healthy

    # 'app' está en AMBAS redes:
    # - backend:  para hablar con db
    # - frontend: para recibir tráfico de nginx
    networks:
      - backend
      - frontend

    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # ── SERVICIO: nginx (Reverse Proxy) ───────────────────────────────────────
  nginx:
    image: nginx:1.25-alpine
    container_name: tareas-nginx
    restart: unless-stopped

    # Exponer el puerto al host.
    # ':-80' = valor por defecto si NGINX_PORT no está definido en .env
    ports:
      - "${NGINX_PORT:-80}:80"

    volumes:
      # Montar nuestra configuración de nginx.
      # ':ro' = read-only: nginx lee la config pero no puede modificarla.
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro

    # Nginx solo necesita estar en la red frontend para hablar con app.
    networks:
      - frontend

    # Nginx no inicia hasta que app esté healthy.
    depends_on:
      app:
        condition: service_healthy

# ── REDES ──────────────────────────────────────────────────────────────────────
# Dos redes para segmentar el tráfico:
# - frontend: nginx <→ app   (tráfico HTTP de usuarios)
# - backend:  app   <→ db    (tráfico de base de datos)
# db nunca está expuesta directamente al exterior.
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

# ── VOLÚMENES ──────────────────────────────────────────────────────────────────
# Declaración de volúmenes nombrados a nivel de stack.
# Compose los crea automáticamente si no existen.
volumes:
  postgres-data:
    driver: local
```

---

## Paso 4 — Comandos Esenciales de Docker Compose

### 4.1 Levantar el stack

```bash
cd ~/lab3

# Construir imágenes Y levantar todos los servicios en background
# -d = detached (background)
docker compose up -d

# Forzar rebuild de imágenes aunque ya existan
docker compose up -d --build

# Levantar solo servicios específicos
docker compose up -d db app

# Ver el estado de todos los servicios
docker compose ps

# Ver logs de todos los servicios juntos
docker compose logs

# Ver logs en tiempo real de todos los servicios
docker compose logs -f

# Ver logs solo del servicio app
docker compose logs -f app

# Ver las últimas 50 líneas del servicio db
docker compose logs --tail 50 db
```

---

### 4.2 Operar servicios individuales

```bash
# Ejecutar un comando en un servicio en ejecución
docker compose exec db psql -U admin -d tareas_db
# Dentro de psql: \dt para listar tablas, SELECT * FROM tareas;

# Ejecutar bash en el contenedor de la app
docker compose exec app bash

# Reiniciar solo nginx (después de cambiar su configuración)
docker compose restart nginx

# Escalar el servicio app a 3 réplicas
# (requiere no tener container_name fijo y usar ports con rango)
docker compose up -d --scale app=3

# Ver procesos de todos los contenedores del stack
docker compose top
```

---

### 4.3 Detener y limpiar

```bash
# Detener todos los servicios (NO los elimina)
docker compose stop

# Iniciar servicios detenidos
docker compose start

# Detener Y ELIMINAR contenedores + redes del stack
# Los volúmenes y las imágenes NO se eliminan
docker compose down

# Eliminar también los volúmenes nombrados (borra datos de la BD)
docker compose down -v

# Eliminar también las imágenes construidas con 'build:'
docker compose down --rmi local

# Eliminación total: contenedores + redes + volúmenes + imágenes
docker compose down -v --rmi all
```

| Comando | Explicación |
|---------|-------------|
| `docker compose up -d` | Levanta el stack completo en background. Construye imágenes si no existen. |
| `docker compose down` | Limpia el stack. Sin `-v` conserva los datos en volúmenes nombrados. |
| `docker compose exec svc cmd` | Como `docker exec` pero por nombre de servicio, no de contenedor. |
| `docker compose logs -f svc` | Streaming de logs de un servicio específico. Esencial para debugging. |
| `docker compose ps` | Estado resumido: nombre, imagen, estado, puertos. |

---

## Paso 5 — Verificar el Stack

```bash
# Con todo el stack levantado:

# 1. Verificar estado de los servicios
docker compose ps
# Todos deben mostrar: Up (healthy)

# 2. Verificar que nginx responde
curl http://localhost:80

# 3. Crear una tarea via la API
curl -X POST http://localhost/tareas \
     -H 'Content-Type: application/json' \
     -d '{"titulo": "Tarea desde Lab 3"}'

# 4. Verificar en la base de datos directamente
docker compose exec db psql -U admin -d tareas_db \
  -c 'SELECT * FROM tareas;'

# 5. Ver el health de cada contenedor
docker inspect tareas-db --format '{{.State.Health.Status}}'
docker inspect tareas-app --format '{{.State.Health.Status}}'

# 6. Verificar las redes
docker network ls | grep lab3
docker network inspect lab3_backend
```

---

## Resumen del Laboratorio 3

| Concepto | Función |
|----------|---------|
| `version / services / networks / volumes` | Cuatro bloques principales del `docker-compose.yml`. |
| `image:` vs `build:` | Usar imagen pre-existente vs construir desde Dockerfile. |
| `environment:` con `.env` | Separar configuración del código. Variables nunca hardcodeadas. |
| `depends_on: condition: service_healthy` | Orden de inicio correcto basado en healthchecks. |
| Redes `frontend` / `backend` | Segmentación: nginx no puede acceder a `db` directamente. |
| Volúmenes nombrados | Persistencia de datos independiente del ciclo del contenedor. |
| `docker compose up/down/logs/exec` | Comandos esenciales del ciclo de vida de un stack Compose. |

---

---

# LABORATORIO 4 — Producción: Healthchecks, Backups y Seguridad

El laboratorio final integra todos los conceptos del curso y aplica prácticas de producción real: monitoreo de salud, backups automatizados de la base de datos, límites de recursos, seguridad de contenedores y registro de logs.

## Objetivo

- Implementar y verificar healthchecks completos.
- Automatizar backups de PostgreSQL con `docker exec` y `docker cp`.
- Aplicar límites de recursos (CPU y memoria).
- Endurecer la seguridad de los contenedores (`read-only`, capabilities, `no-new-privileges`).
- Configurar logging drivers y rotación de logs.
- Exportar e importar imágenes con `docker save` y `docker load`.

---

## Paso 1 — Healthchecks en Profundidad

### 1.1 Estados posibles de salud

| Estado | Descripción |
|--------|-------------|
| `starting` | Estado inicial. Docker aún no ha ejecutado el primer check (respeta `start_period`). |
| `healthy` | El check pasó exitosamente el número mínimo de veces. |
| `unhealthy` | El check falló `retries` veces consecutivas. Docker puede reiniciar el contenedor. |
| `none` | No hay `HEALTHCHECK` definido. El contenedor nunca reporta estado de salud. |

---

### 1.2 Healthcheck completo en `docker-compose.yml`

```yaml
# ~/lab4/docker-compose.yml (fragmento del servicio db)

  db:
    image: postgres:15-alpine
    container_name: tareas-db
    restart: unless-stopped
    environment:
      POSTGRES_DB:       ${POSTGRES_DB}
      POSTGRES_USER:     ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    healthcheck:
      # pg_isready verifica que PostgreSQL acepta conexiones.
      # CMD-SHELL permite usar variables de entorno y operadores shell (&&, ||)
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s      # Verificar cada 10 segundos
      timeout: 5s        # Si no responde en 5s → fallo
      retries: 5         # 5 fallos seguidos → unhealthy
      start_period: 30s  # Ignorar fallos los primeros 30s (PostgreSQL tarda en iniciar)

  app:
    build: .
    container_name: tareas-app
    restart: unless-stopped
    environment:
      DB_HOST:  db
      DB_NAME:  ${POSTGRES_DB}
      DB_USER:  ${POSTGRES_USER}
      DB_PASS:  ${POSTGRES_PASSWORD}
    depends_on:
      db:
        condition: service_healthy   # Espera a que db esté healthy
    networks:
      - backend
      - frontend
    healthcheck:
      # wget es más ligero que curl. -q = quiet, -O- = output to stdout
      # || exit 1 → si wget falla, devuelve código de salida 1 (fallo)
      test: ["CMD-SHELL", "wget -qO- http://localhost:5000/ > /dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

### 1.3 Inspeccionar el estado de salud

```bash
# Ver el estado resumido de todos los contenedores
docker compose ps
# La columna 'STATUS' mostrará: Up (healthy), Up (unhealthy), Up (starting)

# Ver el estado de salud detallado de un contenedor específico
docker inspect tareas-db --format '{{json .State.Health}}' | python3 -m json.tool

# Ver solo el status
docker inspect tareas-db --format '{{.State.Health.Status}}'

# Ver el log de los últimos checks (hasta 5 por defecto)
docker inspect tareas-db \
  --format '{{range .State.Health.Log}}{{.Output}}{{end}}'

# Ver cuándo fue el último check y el streak de fallos
docker inspect tareas-app \
  --format 'Status: {{.State.Health.Status}} | FailStreak: {{.State.Health.FailingStreak}}'
```

---

## Paso 2 — Backups de Base de Datos

### 2.1 Backup manual con `pg_dump`

`pg_dump` es la herramienta oficial de PostgreSQL para exportar bases de datos. La ejecutamos dentro del contenedor con `docker exec`:

```bash
# Crear directorio local para los backups
mkdir -p ~/lab4/backups

# MÉTODO 1: docker exec + pg_dump directo
# Ejecuta pg_dump dentro del contenedor y guarda la salida en el host
#
# -U admin       → usuario de PostgreSQL
# -d tareas_db   → nombre de la base de datos
# -F c           → formato custom (comprimido, restaurable con pg_restore)
#
# > ~/lab4/backups/... → redirige la salida estándar al archivo local
docker exec tareas-db pg_dump \
  -U admin \
  -d tareas_db \
  -F c \
  > ~/lab4/backups/backup-$(date +%Y%m%d-%H%M%S).dump

# Verificar que el backup se creó
ls -lh ~/lab4/backups/

# MÉTODO 2: Formato SQL plano (más legible, menos eficiente)
docker exec tareas-db pg_dump \
  -U admin \
  -d tareas_db \
  --format=plain \
  > ~/lab4/backups/backup-$(date +%Y%m%d).sql

# Ver las primeras líneas del backup SQL
head -30 ~/lab4/backups/backup-$(date +%Y%m%d).sql
```

| Opción | Explicación |
|--------|-------------|
| `pg_dump` | Herramienta de PostgreSQL para exportar la estructura y datos de una BD. |
| `-F c` | Formato custom: comprimido y permite restauración selectiva de tablas. |
| `-F p` | Formato plain SQL: legible pero más grande. Útil para revisar manualmente. |
| `$(date +...)` | Bash: inserta la fecha actual en el nombre del archivo. Ej: `20250120-143000`. |
| `> archivo` | Redirección: la salida de `pg_dump` se escribe al archivo en el host. |

---

### 2.2 Backup adicional con `docker cp`

Para complementar, también podemos usar `docker cp` para copiar archivos de configuración o hacer un snapshot del volumen:

```bash
# Copiar archivos de configuración del contenedor al host
docker cp tareas-db:/etc/postgresql/postgresql.conf \
  ~/lab4/backups/postgresql.conf.bak 2>/dev/null || echo 'Archivo no encontrado'

# Para backup del volumen completo: detener la db, copiar el volumen
docker compose stop db
docker run --rm \
  -v lab3_postgres-data:/data \
  -v ~/lab4/backups:/backup \
  alpine tar czf /backup/pgdata-$(date +%Y%m%d).tar.gz -C /data .
docker compose start db

# Verificar el backup del volumen
ls -lh ~/lab4/backups/*.tar.gz
```

---

### 2.3 Restaurar desde un backup

```bash
# RESTAURAR desde formato custom (.dump)
# 1. Crear base de datos nueva (o limpiar la existente)
docker exec tareas-db createdb -U admin tareas_db_restored

# 2. Copiar el backup al contenedor
BACKUP_FILE=~/lab4/backups/backup-20250120-143000.dump   # ajustar nombre
docker cp $BACKUP_FILE tareas-db:/tmp/restore.dump

# 3. Restaurar con pg_restore
docker exec tareas-db pg_restore \
  -U admin \
  -d tareas_db_restored \
  -F c \
  /tmp/restore.dump

# 4. Verificar la restauración
docker exec tareas-db psql -U admin -d tareas_db_restored \
  -c 'SELECT count(*) FROM tareas;'

# RESTAURAR desde formato SQL plano
docker cp ~/lab4/backups/backup-$(date +%Y%m%d).sql tareas-db:/tmp/restore.sql
docker exec tareas-db psql -U admin -d tareas_db -f /tmp/restore.sql
```

---

### 2.4 Script de backup automatizado

En producción los backups se automatizan con cron. Guarda este script y agrégalo al crontab:

```bash
#!/bin/bash
# ~/lab4/backup.sh
# Agregar a cron con: crontab -e
# Línea de cron: 0 2 * * * /bin/bash ~/lab4/backup.sh
# (Corre cada día a las 2:00 AM)

BACKUP_DIR=~/lab4/backups
FECHA=$(date +%Y%m%d-%H%M%S)
CONTENEDOR=tareas-db
DB_USER=admin
DB_NAME=tareas_db
RETENTION_DIAS=7   # eliminar backups con más de 7 días

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Verificar que el contenedor está corriendo y healthy
STATUS=$(docker inspect $CONTENEDOR --format '{{.State.Health.Status}}' 2>/dev/null)
if [ "$STATUS" != "healthy" ]; then
    echo "[ERROR] Contenedor $CONTENEDOR no está healthy. Status: $STATUS"
    exit 1
fi

# Ejecutar backup
docker exec $CONTENEDOR pg_dump -U $DB_USER -d $DB_NAME -F c \
  > $BACKUP_DIR/backup-${FECHA}.dump

if [ $? -eq 0 ]; then
    echo "[OK] Backup creado: backup-${FECHA}.dump"
else
    echo "[ERROR] Fallo al crear backup"
    exit 1
fi

# Eliminar backups más antiguos que RETENTION_DIAS
find $BACKUP_DIR -name '*.dump' -mtime +$RETENTION_DIAS -delete
echo "[OK] Backups antiguos eliminados (retención: $RETENTION_DIAS días)"
```

---

## Paso 3 — Límites de Recursos

Sin límites, un contenedor puede consumir toda la CPU y RAM del host, afectando otros servicios. Docker permite establecer límites para garantizar la estabilidad:

### 3.1 Límites en `docker run`

```bash
# Limitar CPU: máximo 0.5 CPUs (50% de un core)
# Limitar RAM: máximo 256 megabytes
docker run -d \
  --name app-limitada \
  --cpus 0.5 \
  --memory 256m \
  --memory-swap 256m \
  -p 5001:5000 \
  gestor-tareas:v1.0

# Verificar los límites aplicados
docker inspect app-limitada --format \
  'CPU: {{.HostConfig.NanoCpus}} | Mem: {{.HostConfig.Memory}}'

# Ver consumo en tiempo real
docker stats app-limitada --no-stream
```

| Flag | Explicación |
|------|-------------|
| `--cpus 0.5` | 0.5 = 50% de 1 CPU. El contenedor no puede usar más de medio núcleo. |
| `--memory 256m` | Límite de RAM. Si lo supera, el proceso es killed (OOM - Out Of Memory). |
| `--memory-swap 256m` | Igual que `--memory` → deshabilita el swap. |

---

### 3.2 Límites en `docker-compose.yml`

```yaml
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.50'     # máximo 50% de 1 CPU
          memory: 256M     # máximo 256 MB de RAM
        reservations:
          cpus: '0.25'     # garantizar al menos 25% de CPU
          memory: 128M     # garantizar al menos 128 MB

  db:
    image: postgres:15-alpine
    deploy:
      resources:
        limits:
          cpus: '1.00'
          memory: 512M
        reservations:
          cpus: '0.50'
          memory: 256M
```

> **NOTA:** El bloque `deploy:` en `docker-compose.yml` es respetado por Docker Compose en modo standalone desde la versión 3.x.

---

## Paso 4 — Endurecimiento de Seguridad

### 4.1 Filesystem de solo lectura

```bash
# --read-only: el filesystem raíz del contenedor es de solo lectura
# --tmpfs /tmp: permite escritura solo en /tmp (en RAM, temporal)
# Si la app intenta escribir fuera de /tmp o /app/data → error de permiso
docker run -d \
  --name app-ro \
  --read-only \
  --tmpfs /tmp \
  -v datos-app:/app/data \
  gestor-tareas:v1.0

# Verificar que es read-only
docker exec app-ro touch /etc/hack 2>&1
# Debe devolver: touch: /etc/hack: Read-only file system
```

---

### 4.2 Linux Capabilities

Los contenedores heredan un conjunto de Linux Capabilities por defecto. La práctica de seguridad es eliminarlas todas y agregar solo las necesarias (principio de mínimo privilegio):

```bash
# --cap-drop ALL: eliminar TODAS las capabilities Linux
# --cap-add NET_BIND_SERVICE: agregar solo la de escuchar en puertos < 1024
docker run -d \
  --name app-caps \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  gestor-tareas:v1.0

# --security-opt no-new-privileges:true
# Impide que procesos dentro del contenedor escalen privilegios
# (via setuid binaries como sudo).
# Muy importante para contenedores de producción.
docker run -d \
  --name app-secure \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --read-only \
  --tmpfs /tmp \
  gestor-tareas:v1.0
```

| Flag | Explicación |
|------|-------------|
| `--cap-drop ALL` | Elimina todas las capabilities. Nada de privilegios por defecto. |
| `--cap-add NET_BIND_SERVICE` | Agrega capacidad de escuchar en puertos < 1024 (como el 80). |
| `--security-opt no-new-privileges:true` | Bloquea escalada de privilegios via setuid/setgid. Estándar en producción. |
| `--read-only` | Filesystem root del contenedor es inmutable. Reduce superficie de ataque. |

---

### 4.3 Seguridad en `docker-compose.yml`

```yaml
  app:
    build: .
    container_name: tareas-app
    restart: unless-stopped

    # Bloquear escalada de privilegios
    security_opt:
      - no-new-privileges:true

    # Eliminar todas las capabilities excepto las necesarias
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

    # Filesystem de solo lectura
    read_only: true

    # Directorios donde la app necesita escribir
    tmpfs:
      - /tmp:noexec,nosuid,size=64m
      # noexec: no ejecutar binarios desde /tmp
      # nosuid: ignorar bits setuid
      # size=64m: limitar a 64MB en RAM

  db:
    image: postgres:15-alpine
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - SETUID        # PostgreSQL necesita cambiar de usuario
      - SETGID
      - DAC_OVERRIDE  # Acceso a archivos de datos
```

---

## Paso 5 — Logging y Rotación de Logs

### 5.1 Configurar el logging driver

Por defecto Docker usa el driver `json-file` que escribe logs en disco. Sin límites puede llenar el disco del host:

```bash
# Ver el driver de logs actual de un contenedor
docker inspect tareas-app --format '{{.HostConfig.LogConfig.Type}}'

# Lanzar contenedor con logs limitados:
# max-size: tamaño máximo de cada archivo de log
# max-file: número máximo de archivos de log rotados
docker run -d \
  --name app-logs \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  gestor-tareas:v1.0
# Esto mantiene máximo 3 archivos de 10MB = 30MB máximo de logs

# Ruta de los logs en el host
docker inspect app-logs --format '{{.LogPath}}'
```

---

### 5.2 Logging en `docker-compose.yml`

```yaml
  app:
    build: .
    logging:
      driver: json-file         # Driver: json-file, syslog, journald, none, etc.
      options:
        max-size: '10m'         # Rotar cuando el archivo supere 10MB
        max-file: '3'           # Mantener máximo 3 archivos rotados

  db:
    image: postgres:15-alpine
    logging:
      driver: json-file
      options:
        max-size: '5m'
        max-file: '5'

  nginx:
    image: nginx:1.25-alpine
    logging:
      driver: json-file
      options:
        max-size: '20m'         # Nginx genera más logs de acceso
        max-file: '5'
```

---

## Paso 6 — Exportar e Importar Imágenes

`docker save` y `docker load` permiten transferir imágenes sin un registry. Útil para entornos sin internet, air-gapped, o para compartir imágenes entre máquinas:

### 6.1 Exportar imágenes con `docker save`

```bash
# Exportar una imagen a un archivo .tar
# -o output: especificar el archivo de salida
docker save -o ~/lab4/gestor-tareas-v1.tar gestor-tareas:v1.0

# Ver el tamaño del archivo exportado
ls -lh ~/lab4/gestor-tareas-v1.tar

# Comprimir para ahorrar espacio
docker save gestor-tareas:v1.0 | gzip > ~/lab4/gestor-tareas-v1.tar.gz
ls -lh ~/lab4/gestor-tareas-v1.tar.gz

# Exportar MÚLTIPLES imágenes en un solo archivo
docker save -o ~/lab4/stack-completo.tar \
  gestor-tareas:v1.0 \
  nginx:1.25-alpine \
  postgres:15-alpine

# Exportar solo el filesystem del CONTENEDOR (no la imagen)
# Diferencia: 'export' = contenedor en ejecución, 'save' = imagen con capas
docker export tareas-app -o ~/lab4/app-container.tar
```

| Comando | Explicación |
|---------|-------------|
| `docker save` | Exporta una o más imágenes con **todas sus capas** y metadatos. Restaurable con `docker load`. |
| `docker export` | Exporta el filesystem de un contenedor como snapshot plano (sin capas). Solo para casos especiales. |
| `gzip` | Compresión estándar. Reduce el `.tar` considerablemente (hasta 40-60% menos). |

---

### 6.2 Importar imágenes con `docker load`

```bash
# ESCENARIO: transferir imagen a otro servidor sin Docker Hub

# En el servidor DESTINO, cargar la imagen desde el .tar
docker load -i ~/lab4/gestor-tareas-v1.tar

# Cargar imagen comprimida directamente
docker load < ~/lab4/gestor-tareas-v1.tar.gz

# Verificar que la imagen fue cargada correctamente
docker images | grep gestor-tareas

# La imagen ya está disponible para crear contenedores
docker run -d --name app-importada -p 5002:5000 gestor-tareas:v1.0
```

---

## Paso 7 — Docker Compose Final de Producción

Integramos todo lo aprendido en los 4 laboratorios en un único archivo listo para producción:

```yaml
# ~/lab4/docker-compose.prod.yml
# Stack completo con: healthchecks, límites de recursos,
# seguridad, logging configurado y restart policies.

version: '3.9'

services:

  db:
    image: postgres:15-alpine
    container_name: tareas-db
    restart: unless-stopped
    environment:
      POSTGRES_DB:       ${POSTGRES_DB}
      POSTGRES_USER:     ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '1.00'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - SETUID
      - SETGID
      - DAC_OVERRIDE
    logging:
      driver: json-file
      options:
        max-size: '5m'
        max-file: '5'

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: tareas-app
    restart: unless-stopped
    environment:
      DB_HOST:    db
      DB_NAME:    ${POSTGRES_DB}
      DB_USER:    ${POSTGRES_USER}
      DB_PASS:    ${POSTGRES_PASSWORD}
      FLASK_ENV:  production
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend
      - frontend
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:5000/ > /dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=64m
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'

  nginx:
    image: nginx:1.25-alpine
    container_name: tareas-nginx
    restart: unless-stopped
    ports:
      - '${NGINX_PORT:-80}:80'
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - frontend
    depends_on:
      app:
        condition: service_healthy
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    logging:
      driver: json-file
      options:
        max-size: '20m'
        max-file: '5'

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

volumes:
  postgres-data:
    driver: local
```

---

## Paso 8 — Checklist de Despliegue en Producción

Antes de llevar un stack Docker a producción, verifica estos puntos:

1. Healthchecks definidos en todos los servicios críticos.
2. Restart policy configurada (`unless-stopped` o `on-failure`).
3. Variables sensibles en archivo `.env`, nunca hardcodeadas.
4. `.env` en `.gitignore` y `.dockerignore`.
5. Límites de CPU y memoria establecidos para cada servicio.
6. Usuario no-root definido en el Dockerfile (`USER appuser`).
7. `--security-opt no-new-privileges:true` en todos los servicios.
8. `cap_drop: ALL` + solo las capabilities necesarias agregadas.
9. Logging driver configurado con rotación (`max-size`, `max-file`).
10. Backups automatizados con script y política de retención.
11. Imágenes exportadas con `docker save` para disaster recovery.
12. Redes segmentadas: servicios no expuestos directamente al exterior.

---

## Resumen del Laboratorio 4

| Concepto / Comando | Función |
|--------------------|---------|
| `HEALTHCHECK` (Dockerfile y Compose) | Monitoreo de salud: `starting` → `healthy` / `unhealthy`. |
| `docker exec + pg_dump` | Backup de PostgreSQL ejecutando herramienta nativa dentro del contenedor. |
| `docker cp` | Backup de archivos individuales del contenedor al host. |
| `--cpus / --memory / deploy.resources` | Límites de recursos para garantizar estabilidad del host. |
| `--cap-drop ALL + --cap-add` | Mínimo privilegio: eliminar capabilities innecesarias. |
| `--security-opt no-new-privileges` | Bloquear escalada de privilegios desde dentro del contenedor. |
| `--read-only + tmpfs` | Filesystem inmutable excepto directorios explícitamente permitidos. |
| Logging driver + `max-size` | Evitar que los logs llenen el disco del host. |
| `docker save / docker load` | Transportar imágenes sin registry. Disaster recovery offline. |

---

---

# REFERENCIA RÁPIDA — Todos los Comandos del Curso

## Comandos Docker CLI

| Comando | Función |
|---------|---------|
| `docker pull <imagen>` | Descargar imagen desde Docker Hub. |
| `docker images / image ls` | Listar imágenes locales. |
| `docker image inspect <img>` | Información completa de una imagen en JSON. |
| `docker tag <src> <dest>` | Crear alias/tag para una imagen. |
| `docker rmi <imagen>` | Eliminar una imagen local. |
| `docker run -d -p -v --name` | Crear y ejecutar un contenedor. |
| `docker ps / ps -a` | Ver contenedores activos / todos. |
| `docker stop / start / restart` | Detener, iniciar, reiniciar contenedor. |
| `docker rm / rm -f` | Eliminar contenedor parado / forzado. |
| `docker exec -it <name> bash` | Abrir shell en contenedor en ejecución. |
| `docker logs -f <name>` | Seguir logs de un contenedor en tiempo real. |
| `docker stats` | CPU y RAM en tiempo real. |
| `docker inspect <name>` | JSON completo de un contenedor. |
| `docker cp <src> <dest>` | Copiar archivos host ↔ contenedor. |
| `docker volume create/ls/rm` | Gestionar volúmenes nombrados. |
| `docker network create/ls/rm` | Gestionar redes. |
| `docker system prune -a` | Limpiar todo lo no utilizado. |
| `docker save -o / docker load -i` | Exportar/importar imágenes como `.tar`. |

## Comandos `docker build`

| Comando | Función |
|---------|---------|
| `docker build -t nombre:tag .` | Construir imagen desde Dockerfile en directorio actual. |
| `docker build -f Dockerfile.custom .` | Usar un Dockerfile con nombre personalizado. |
| `docker build --no-cache .` | Construir sin reutilizar caché. |
| `docker build --build-arg CLAVE=val .` | Pasar variable `ARG` al build. |
| `docker history <imagen>` | Ver capas y tamaños de una imagen. |

## Comandos Docker Compose

| Comando | Función |
|---------|---------|
| `docker compose up -d` | Levantar stack en background. |
| `docker compose up -d --build` | Rebuild de imágenes + levantar. |
| `docker compose down` | Detener y eliminar contenedores + redes. |
| `docker compose down -v` | También eliminar volúmenes. |
| `docker compose ps` | Estado de todos los servicios. |
| `docker compose logs -f` | Logs en tiempo real de todo el stack. |
| `docker compose logs -f <svc>` | Logs en tiempo real de un servicio. |
| `docker compose exec <svc> cmd` | Ejecutar comando en servicio activo. |
| `docker compose restart <svc>` | Reiniciar un servicio específico. |
| `docker compose stop/start` | Detener/iniciar sin eliminar contenedores. |
| `docker compose top` | Ver procesos de todos los contenedores. |
| `docker compose build` | Solo construir imágenes sin levantar. |

---

*Universidad Nacional de Ingeniería — OTI-UNI SOC · Lima, Perú*