# Sesion 1: App Flask en Docker

## Estructura

```text
sesion1/
  sin-docker/           # Ejemplo sin Docker (comparacion)
    app.py
    README.md
  app.py                # App Flask para Docker
  requirements.txt      # Dependencias versionadas
  Dockerfile            # Receta para construir la imagen
```

## Prueba 1: Sin Docker

Ver [`sin-docker/`](./sin-docker/) para ejecutar la app directamente en el sistema operativo.

```bash
cd sin-docker
pip install flask
python app.py
```

## Prueba 2: Con Docker

```bash
docker build -t mi-flask:v1 .
docker run --name flask-demo -d -p 5000:5000 mi-flask:v1
```

Abrir `http://localhost:5000`

## Comparacion

| Sin Docker | Con Docker |
|---|---|
| Necesito instalar Python | Docker trae Python dentro |
| Necesito instalar Flask | Docker instala Flask automaticamente |
| Puede funcionar distinto en cada PC | Funciona igual en cualquier PC con Docker |
| Depende del entorno local | Entorno aislado |
| Configuracion manual | Configuracion definida en Dockerfile |
