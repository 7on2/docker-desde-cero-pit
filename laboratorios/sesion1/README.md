# Laboratorio Sesion 1: Contenedores Desde Cero

## Objetivo

Validar la instalacion de Docker, ejecutar contenedores de prueba, construir una imagen propia desde una app Flask y ejecutarla publicando el puerto 5000.

## Archivos

Codigo base: [`../../codigo/sesion1`](../../codigo/sesion1/)

```text
codigo/sesion1/
  app.py
  requirements.txt
  Dockerfile
```

## Paso 1: Validar Docker

```bash
docker --version
docker info
docker run hello-world
```

## Paso 2: Ejecutar Nginx de prueba

```bash
docker run --name web-demo -d -p 8080:80 nginx
docker ps
```

Abrir `http://localhost:8080`

## Paso 3: Detener y limpiar Nginx

```bash
docker stop web-demo
docker ps -a
docker rm web-demo
docker images
```

## Paso 4: Construir imagen Flask

```bash
cd codigo/sesion1
docker build -t mi-flask:v1 .
docker images
```

## Paso 5: Ejecutar la app Flask

```bash
docker run --name flask-demo -d -p 5000:5000 mi-flask:v1
docker ps
```

Abrir `http://localhost:5000`

Resultado esperado:
```text
Hola Docker desde PIT 2026
```

## Paso 6: Revisar logs

```bash
docker logs flask-demo
```

## Paso 7: Limpiar

```bash
docker stop flask-demo
docker rm flask-demo
docker rmi mi-flask:v1
```

## Errores Frecuentes

| Error | Causa | Solucion |
|---|---|---|
| Puerto ocupado | Otro proceso usa 5000 | Usar `-p 5001:5000` |
| No abre en navegador | Contenedor detenido | Revisar `docker ps -a` y `docker logs` |
| Build falla | Archivo faltante | Verificar carpeta y Dockerfile |
| Nombre en uso | Contenedor existente con ese nombre | `docker rm` o usar otro nombre |

## Checklist

- Docker esta instalado y responde
- Se ejecuto un contenedor Nginx y se accedio por el navegador
- Se detuvo y elimino el contenedor correctamente
- Se construyo una imagen propia con `docker build`
- Se ejecuto la app Flask con puerto publicado
- Se limpio el contenedor y la imagen

---

[Volver a clases](../../clases/)
