# Laboratorio Sesion 2: Dockerfile, Imagenes y Docker Hub

## Objetivo

Construir una imagen profesional de una app Flask usando Dockerfile, `.dockerignore`, tags, revision de capas y publicacion en Docker Hub.

## Archivos

Codigo base: [`../../codigo/sesion2`](../../codigo/sesion2/)

```text
codigo/sesion2/
  app.py
  requirements.txt
  Dockerfile
  Dockerfile.multistage
  Dockerfile.slim
  Dockerfile.alpine
  .dockerignore
```

## Paso 1: Construir imagen versionada

```bash
cd codigo/sesion2
docker build -t mi-flask:v1 .
docker run -d --name flask-v1 -p 5000:5000 mi-flask:v1
curl http://localhost:5000
docker stop flask-v1
docker rm flask-v1
```

## Paso 2: Revisar capas

```bash
docker history mi-flask:v1
```

## Paso 3: Demostrar cache

```bash
# Segunda construccion (mas rapida)
docker build -t mi-flask:v1 .

# Cambiar app.py y reconstruir
docker build -t mi-flask:v2 .
```

## Paso 4: Capa escribible

```bash
docker run -it --name prueba-escritura mi-flask:v1 sh
echo "archivo temporal" > temporal.txt
ls
exit

docker rm prueba-escritura

docker run -it --name prueba-escritura-2 mi-flask:v1 sh
ls
# temporal.txt no aparece
exit

docker rm prueba-escritura-2
```

## Paso 5: Multistage build

```bash
docker build -f Dockerfile.multistage -t mi-flask:multi .

# Comparar tamanos
docker images | grep mi-flask
docker history mi-flask:v2
docker history mi-flask:multi
```

## Paso 6: Comparar slim vs alpine

```bash
docker build -f Dockerfile.slim -t flask:slim .
docker build -f Dockerfile.alpine -t flask:alpine .
docker images | grep flask
```

## Paso 7: Etiquetar para Docker Hub

Reemplaza `tuusuario` por tu usuario real de Docker Hub.

```bash
docker tag mi-flask:v2 tuusuario/mi-flask:v2
```

## Paso 8: Publicar

```bash
docker login
docker push tuusuario/mi-flask:v2
```

## Paso 9: Probar pull

```bash
docker stop flask-v2 2>/dev/null; docker rm flask-v2 2>/dev/null
docker rmi mi-flask:v2 2>/dev/null
docker rmi tuusuario/mi-flask:v2 2>/dev/null

docker pull tuusuario/mi-flask:v2
docker run -d --name flask-remoto -p 5000:5000 tuusuario/mi-flask:v2
curl http://localhost:5000
docker stop flask-remoto
docker rm flask-remoto
```

## Checklist

- El Dockerfile usa imagen base especifica
- Las dependencias se instalan antes de copiar el codigo cambiante
- `.dockerignore` evita enviar `.git`, `.env`, caches y archivos innecesarios
- La imagen tiene tag versionado
- Se revisaron las capas con `docker history`
- Se entendio la capa escribible del contenedor
- Se comparo multistage vs Dockerfile normal
- Se comparo slim vs alpine
- Se etiqueto y publico la imagen en Docker Hub

---

[Volver a clases](../../clases/)
