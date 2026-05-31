# Laboratorio Sesion 2: Dockerfile Profesional

## Objetivo

Optimizar el Dockerfile de la app Flask, usar `.dockerignore`, construir una imagen versionada y preparar el flujo de publicacion.

## Archivos

Codigo base: [`../../codigo/sesion2`](../../codigo/sesion2/)

```text
codigo/sesion2/
  app.py
  requirements.txt
  Dockerfile
  .dockerignore
```

## Construir Imagen

```bash
cd codigo/sesion2
docker build -t mi-flask:v2 .
docker history mi-flask:v2
docker images
```

## Ejecutar Y Probar

```bash
docker run -d --name flask-v2 -p 5000:5000 mi-flask:v2
curl http://localhost:5000
```

## Tagging Para Registro

Reemplaza `tuusuario` por tu usuario real de Docker Hub.

```bash
docker login
docker tag mi-flask:v2 tuusuario/mi-flask:v2
docker push tuusuario/mi-flask:v2
```

## Limpieza

```bash
docker stop flask-v2
docker rm flask-v2
```

## Checklist

- El Dockerfile usa imagen base especifica.
- Las dependencias se instalan antes de copiar el codigo cambiante.
- `.dockerignore` evita enviar `.git`, `.env`, caches y archivos innecesarios.
- La imagen tiene tag versionado.
