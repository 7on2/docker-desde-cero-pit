# Sesion 1: Contenedores Desde Cero

## Objetivo

Comprender que problema resuelve Docker, diferenciar imagen y contenedor, ejecutar comandos esenciales y construir una primera aplicacion Flask en contenedor.

## El problema: funciona en mi maquina

Una aplicacion puede funcionar en la laptop del desarrollador y fallar en otro entorno por diferencias de versiones, librerias o configuracion. Docker reduce esa variacion empaquetando la aplicacion con sus dependencias.

```mermaid
flowchart LR
    A["Codigo"] --> B["Dependencias"] --> C["Imagen Docker"] --> D["Contenedor"]
    style A fill:#1f6feb,stroke:#58a6ff,color:#fff
    style B fill:#238636,stroke:#3fb950,color:#fff
    style C fill:#8957e5,stroke:#bc8cff,color:#fff
    style D fill:#9e6a03,stroke:#d29922,color:#fff
```

## Docker vs maquina virtual

Una VM virtualiza una maquina completa e incluye un sistema operativo invitado. Un contenedor comparte el kernel del host y solo incluye lo necesario para ejecutar la aplicacion.

| Criterio | Maquina virtual | Contenedor |
|---|---|---|
| Sistema operativo | Incluye SO completo | Comparte kernel del host |
| Arranque | Mas lento | Rapido |
| Consumo | Mayor RAM y disco | Menor consumo |
| Uso comun | Laboratorios o servidores completos | Apps reproducibles |

## Comandos esenciales

```bash
docker --version
docker info
docker run hello-world
docker run --name web-demo -d -p 8080:80 nginx
docker ps
docker stop web-demo
docker rm web-demo
docker images
```

## Imagen vs contenedor

- Imagen: plantilla inmutable con sistema base, dependencias y codigo.
- Contenedor: instancia en ejecucion creada desde una imagen.

Analogia: la imagen es la receta; el contenedor es el plato servido.

## Primera app Flask

La sesion termina construyendo una app minima con `Dockerfile`, `requirements.txt` y `app.py`.

```bash
cd codigo/sesion1
docker build -t mi-flask:v1 .
docker run --name flask-demo -d -p 5000:5000 mi-flask:v1
```

---

[Siguiente: Dockerfile profesional](./02-dockerfile-profesional.md)
