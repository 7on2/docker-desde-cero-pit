# Lab 1 - Fundamentos Docker CLI

Objetivo: practicar el ciclo de vida de contenedores, transferencia de archivos, volumenes, bind mounts, redes y limpieza.

## Comandos base

```bash
docker pull nginx
docker pull nginx:1.25-alpine
docker pull ubuntu:22.04
docker images
docker image inspect nginx
```

## Contenedores

```bash
docker run hello-world
docker run -d -p 8080:80 --name mi-web nginx
curl http://localhost:8080

docker ps
docker logs mi-web
docker exec mi-web ls /etc/nginx
docker exec -it mi-web sh
docker rm -f mi-web
```

## Bind mount

```bash
docker run -d --name web-dev -p 8083:80 -v "$PWD/html:/usr/share/nginx/html" nginx
curl http://localhost:8083
```

Edita `html/index.html` y vuelve a probar con `curl`.

## Redes

```bash
docker network create --driver bridge red-lab
docker run -d --name servidor --network red-lab nginx
docker run -d --name cliente --network red-lab alpine sleep 3600
docker exec cliente ping -c 3 servidor
```

## Limpieza

```bash
docker rm -f web-dev servidor cliente
docker network rm red-lab
docker system df
```
