# LAB 1 — Fundamentos: Docker CLI desde Cero

En este laboratorio recorreremos los comandos esenciales de Docker: gestión de imágenes, contenedores, redes, volúmenes y transferencia de archivos. Todo se ejecuta directamente desde la terminal, sin escribir aún ningún Dockerfile ni Compose.

## Objetivo

- Comprender el ciclo de vida completo de un contenedor.
- Dominar `docker run`, `docker ps`, `docker exec`, `docker cp`.
- Gestionar imágenes locales: `pull`, `tag`, `rmi`, `inspect`.
- Crear y usar redes y volúmenes desde la CLI.

---

## Conceptos Clave

| Término | Descripción |
|---------|-------------|
| **Imagen** | Plantilla de solo lectura. Es el "molde" del contenedor. Ej: `nginx:latest` |
| **Contenedor** | Instancia en ejecución de una imagen. Tiene su propio filesystem, red y proceso. |
| **Docker Daemon** | Proceso que corre en background y gestiona todo. Se llama `dockerd`. |
| **Registry** | Repositorio de imágenes. El público por defecto es Docker Hub (`hub.docker.com`). |
| **Layer** | Capa del sistema de archivos. Las imágenes se construyen por capas apiladas. |
| **Volume** | Directorio persistente gestionado por Docker, sobrevive al borrado del contenedor. |
| **Bind Mount** | Monta una carpeta real del host dentro del contenedor. Muy útil en desarrollo. |
| **Network** | Red virtual que conecta contenedores entre sí de forma aislada. |

---

## Paso 1 — Gestión de Imágenes

### 1.1 Descargar una imagen con `docker pull`

```bash
docker pull nginx
docker pull nginx:1.25-alpine
docker pull ubuntu:22.04
```

| Comando | Explicación |
|---------|-------------|
| `docker pull nginx` | Descarga `nginx:latest` (el tag `latest` se asume si no se especifica) |
| `docker pull nginx:1.25-alpine` | Descarga la versión exacta 1.25 basada en Alpine Linux (~8MB vs ~50MB) |
| `:alpine` | Variante mínima. Alpine Linux es una distro de ~5MB ideal para producción. |

### 1.2 Listar y explorar imágenes locales

```bash
docker images
docker image ls
docker image inspect nginx
docker image inspect nginx --format '{{.Config.ExposedPorts}}'
```

### 1.3 Etiquetar y eliminar imágenes

```bash
docker tag nginx:latest mi-nginx:v1.0
docker images | grep mi-nginx
docker rmi mi-nginx:v1.0
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

```bash
docker run hello-world
docker run -d -p 8080:80 --name mi-web nginx
curl http://localhost:8080
docker run -it ubuntu:22.04 bash
docker run --rm ubuntu:22.04 echo 'Hola desde contenedor'
```

| Flag | Explicación |
|------|-------------|
| `-d` | *Detached mode*. El contenedor corre en segundo plano. |
| `-p 8080:80` | Mapeo de puertos. El puerto 80 del contenedor queda accesible en el 8080 del host. |
| `--name` | Nombre legible. Sin esto Docker asigna nombres aleatorios. |
| `-it` | `-i` + `-t` combinados. Necesario para shells interactivas. |
| `--rm` | *Auto-remove*. Limpio para contenedores temporales. |

### 2.2 Gestionar contenedores en ejecución

```bash
docker ps
docker ps -a
docker ps -q
docker stop mi-web
docker start mi-web
docker restart mi-web
docker kill mi-web
docker rm mi-web
docker rm -f mi-web
```

### 2.3 Interactuar con contenedores: `exec`, `logs`, `inspect`

```bash
docker run -d -p 8080:80 --name mi-web nginx
docker exec mi-web ls /etc/nginx
docker exec -it mi-web bash
docker logs mi-web
docker logs -f mi-web
docker logs --tail 20 mi-web
docker inspect mi-web
docker inspect mi-web --format '{{.NetworkSettings.IPAddress}}'
docker stats mi-web
```

---

## Paso 3 — Transferencia de Archivos con `docker cp`

```bash
echo '<h1>Docker Labs - UNI</h1>' > index.html
docker cp index.html mi-web:/usr/share/nginx/html/index.html
curl http://localhost:8080

docker cp mi-web:/etc/nginx/nginx.conf ./nginx-backup.conf
cat nginx-backup.conf

docker cp mi-web:/usr/share/nginx/html ./html-backup/
ls ./html-backup/
```

---

## Paso 4 — Volúmenes y Persistencia

### 4.1 Tipos de almacenamiento en Docker

| Tipo | Descripción |
|------|-------------|
| **Volume (nombrado)** | Docker gestiona la ubicación (`/var/lib/docker/volumes/`). Recomendado para bases de datos y producción. |
| **Bind Mount** | Carpeta del host montada en el contenedor. Ideal en desarrollo para editar código en tiempo real. |
| **tmpfs** | Solo en Linux. Almacena en RAM. Datos NO persisten ni siquiera si el contenedor vive. |

### 4.2 Crear y usar volumes nombrados

```bash
docker volume create datos-nginx
docker volume ls
docker volume inspect datos-nginx

docker run -d \
  --name web-persistente \
  -p 8081:80 \
  -v datos-nginx:/usr/share/nginx/html \
  nginx

docker exec web-persistente bash -c \
  "echo '<h1>Persistente!</h1>' > /usr/share/nginx/html/index.html"

docker rm -f web-persistente

docker run -d --name web-nuevo -p 8082:80 \
  -v datos-nginx:/usr/share/nginx/html nginx
curl http://localhost:8082

docker volume rm datos-nginx
docker volume prune
```

### 4.3 Bind Mount en desarrollo

```bash
mkdir -p ~/lab1/html
echo '<h1>Lab Docker - Bind Mount</h1>' > ~/lab1/html/index.html

docker run -d \
  --name web-dev \
  -p 8083:80 \
  -v ~/lab1/html:/usr/share/nginx/html \
  nginx

echo '<h1>Cambio en tiempo real!</h1>' > ~/lab1/html/index.html
curl http://localhost:8083
```

> **TIP:** El bind mount es el método preferido durante el desarrollo. Al guardar código en tu editor de texto en el host, el contenedor lo ve al instante.

---

## Paso 5 — Redes en Docker

### 5.1 Redes por defecto

| Tipo | Descripción |
|------|-------------|
| `bridge` | Red por defecto. Contenedores en la misma bridge custom pueden comunicarse por nombre. |
| `host` | El contenedor comparte la red del host directamente. Sin aislamiento. Solo Linux. |
| `none` | Sin red. El contenedor está completamente aislado. |

### 5.2 Crear y usar redes custom

```bash
docker network ls
docker network create --driver bridge red-lab
docker network inspect red-lab

docker run -d --name servidor --network red-lab nginx
docker run -d --name cliente --network red-lab alpine sleep 3600
docker exec cliente ping -c 3 servidor

docker network connect red-lab mi-web
docker network disconnect red-lab mi-web
docker network rm red-lab
```

> **NOTA:** En la red bridge por defecto **NO** funciona resolución DNS por nombre. En redes custom **SÍ**.

---

## Paso 6 — Limpieza del Sistema

```bash
docker system df
docker container prune
docker image prune
docker system prune
docker system prune -a
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