# Laboratorio Sesion 1: Primera App Flask En Docker

## Objetivo

Construir una imagen Docker desde una app Flask minima y ejecutarla publicando el puerto `5000`.

## Archivos

Codigo base: [`../../codigo/sesion1`](../../codigo/sesion1/)

```text
codigo/sesion1/
  app.py
  requirements.txt
  Dockerfile
```

## Pasos

```bash
cd codigo/sesion1
docker build -t mi-flask:v1 .
docker images
docker run --name flask-demo -d -p 5000:5000 mi-flask:v1
docker ps
```

Abrir en el navegador:

```text
http://localhost:5000
```

Resultado esperado:

```text
Hola Docker desde PIT 2026
```

## Limpieza

```bash
docker stop flask-demo
docker rm flask-demo
```

## Errores Frecuentes

| Error | Causa | Solucion |
|---|---|---|
| Puerto ocupado | Otro proceso usa 5000 | Usar `-p 5001:5000` |
| No abre en navegador | Contenedor detenido | Revisar `docker ps -a` |
| Build falla | Archivo faltante | Verificar carpeta y Dockerfile |
