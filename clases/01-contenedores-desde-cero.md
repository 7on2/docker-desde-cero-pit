# Sesion 1: Contenedores Desde Cero

## Objetivo

Comprender que problema resuelve Docker, diferenciar imagen y contenedor, ejecutar comandos esenciales y construir una primera aplicacion Flask en contenedor.

## El problema: funciona en mi maquina

Una aplicacion puede funcionar en la laptop del desarrollador y fallar en otro entorno por diferencias de versiones, librerias o configuracion. Docker reduce esa variacion empaquetando la aplicacion con sus dependencias.

```text
Codigo -> Dependencias -> Imagen Docker -> Contenedor
```

## Contenerizacion

Contenerizacion es empaquetar la app con sus dependencias y configuracion minima para lograr ejecucion aislada y uniforme.

```text
El contenedor reduce diferencias entre desarrollo, pruebas y produccion.
No elimina todas las diferencias: kernel, arquitectura, variables externas y permisos aun importan.
```

## Docker en una frase

Docker es una herramienta para construir, ejecutar y distribuir contenedores.

Flujo diario:
- **Imagen**: paquete reproducible
- **Contenedor**: ejecucion de la imagen
- **Registro**: lugar para compartir imagenes (Docker Hub)
- **CLI**: herramienta de control

## Docker vs maquina virtual

Una VM virtualiza una maquina completa e incluye un sistema operativo invitado. Un contenedor comparte el kernel del host y solo incluye lo necesario para ejecutar la aplicacion.

| Criterio | Maquina virtual | Contenedor |
|---|---|---|
| Sistema operativo | Incluye SO completo | Comparte kernel del host |
| Arranque | Mas lento | Rapido |
| Consumo | Mayor RAM y disco | Menor consumo |
| Uso comun | Laboratorios o servidores completos | Apps reproducibles |
| Aislamiento | Fuerte (kernel propio) | Proceso aislado (kernel compartido) |

### Hipervisores

| Tipo | Descripcion | Ejemplos |
|---|---|---|
| Tipo 1 | Corre directamente sobre hardware | Proxmox, ESXi |
| Tipo 2 | Corre como aplicacion sobre un SO | VirtualBox, VMware Workstation |

Docker **no** es un hipervisor. Usa aislamiento a nivel de sistema operativo (namespaces y cgroups).

## Que si veremos y que no veremos hoy

| Hoy si | Hoy no |
|---|---|
| Instalar y validar Docker | Kubernetes |
| Diferenciar imagen y contenedor | Redes avanzadas |
| Ejecutar contenedores | Docker Compose |
| Construir una primera imagen | Produccion |
| Publicar puertos | Volumenes |

## Comandos esenciales

### Validar instalacion

```bash
docker --version
docker info
docker run hello-world
```

Si `docker --version` funciona pero `docker info` falla, puede ser que el daemon/engine no este activo.

### Ejecutar un servicio web

```bash
docker run --name web-demo -d -p 8080:80 nginx
docker ps
```

- `--name web-demo`: nombre humano para el contenedor
- `-d`: modo detached (segundo plano)
- `-p 8080:80`: puerto host 8080 hacia puerto contenedor 80
- `nginx`: imagen

Abrir `http://localhost:8080`

### Detener y limpiar

```bash
docker stop web-demo
docker ps -a
docker rm web-demo
docker images
```

Contenedor detenido aun ocupa nombre y metadata. No puedes crear otro contenedor con el mismo nombre hasta borrar o renombrar el anterior. La imagen sigue disponible localmente.

### Mapa rapido de comandos

| Comando | Que hace |
|---|---|
| `docker --version` | Valida la CLI |
| `docker info` | Valida conexion con el Engine |
| `docker run` | Crea y arranca un contenedor |
| `docker ps` | Lista contenedores activos |
| `docker ps -a` | Lista contenedores activos y detenidos |
| `docker stop` | Detiene un contenedor |
| `docker rm` | Elimina un contenedor |
| `docker images` | Lista imagenes locales |
| `docker rmi` | Elimina una imagen |
| `docker logs` | Muestra logs de un contenedor |

## Imagen vs contenedor

- **Imagen**: plantilla inmutable con sistema base, dependencias y codigo.
- **Contenedor**: instancia en ejecucion creada desde una imagen.

Analogia: la imagen es la receta; el contenedor es el plato servido.

```bash
docker run hello-world
```

`docker run` puede descargar automaticamente la imagen si no existe localmente. Puedes crear varios contenedores desde la misma imagen. Si eliminas un contenedor, no necesariamente eliminas la imagen.

## Primera app Flask

### Comparacion: sin Docker vs con Docker

| Sin Docker | Con Docker |
|---|---|
| Necesito instalar Python | Docker trae Python dentro |
| Necesito instalar Flask | Docker instala Flask automaticamente |
| Puede funcionar distinto en cada PC | Funciona igual en cualquier PC con Docker |
| Depende del entorno local | Entorno aislado |
| Configuracion manual | Configuracion definida en Dockerfile |

### Archivos del proyecto

```text
codigo/sesion1/
  app.py
  requirements.txt
  Dockerfile
```

### app.py

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hola Docker desde PIT 2026"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

`host="0.0.0.0"` es clave para que la app escuche dentro del contenedor y sea accesible desde fuera. Si se usa `127.0.0.1` dentro del contenedor, la app puede quedar accesible solo dentro del propio contenedor.

### requirements.txt

```text
flask==3.0.3
```

Fijar versiones mejora reproducibilidad.

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
```

| Instruccion | Para que sirve |
|---|---|
| `FROM python:3.12-slim` | Imagen base con Python |
| `WORKDIR /app` | Carpeta de trabajo dentro de la imagen |
| `COPY requirements.txt .` | Copia dependencias primero (mejor cache) |
| `RUN pip install...` | Instala Flask dentro de la imagen |
| `COPY app.py .` | Copia el codigo de la app |
| `EXPOSE 5000` | Documenta el puerto (no lo publica) |
| `CMD ["python", "app.py"]` | Comando por defecto al arrancar |

### Construir la imagen

```bash
cd codigo/sesion1
docker build -t mi-flask:v1 .
docker images
```

- `-t`: nombre y tag de la imagen
- `.`: contexto de build (carpeta actual)

### Ejecutar la aplicacion

```bash
docker run --name flask-demo -d -p 5000:5000 mi-flask:v1
docker ps
```

Abrir `http://localhost:5000`

Resultado esperado:
```text
Hola Docker desde PIT 2026
```

Si el puerto host 5000 esta ocupado, usar `-p 5001:5000` y abrir `http://localhost:5001`.

### Revisar logs

```bash
docker logs flask-demo
```

### Limpiar el laboratorio

```bash
docker stop flask-demo
docker rm flask-demo
docker rmi mi-flask:v1
```

Borrar imagen es opcional. No se puede borrar una imagen si hay contenedores que dependen de ella, salvo forzar con `-f`.

## Errores frecuentes

| Error | Causa | Solucion |
|---|---|---|
| Puerto ocupado | Otro proceso usa el puerto | Cambiar puerto host: `-p 5001:5000` |
| No abre en navegador | Contenedor detenido | Revisar `docker ps -a` y `docker logs` |
| Build falla | Archivo faltante o carpeta incorrecta | Verificar `pwd`, `ls` y nombres de archivo |
| Imagen no encontrada | Nombre o tag incorrectos | Revisar nombre exacto con `docker images` |
| Nombre de contenedor en uso | Ya existe un contenedor con ese nombre | Borrar el anterior con `docker rm` o usar otro nombre |

## Checklist de aprendizaje

- Puedo explicar que problema resuelve Docker
- Puedo diferenciar una VM de un contenedor
- Se que Docker no es un hipervisor
- Puedo definir que es una imagen
- Puedo definir que es un contenedor
- Se que hace `docker run`
- Se para que sirve `docker ps -a`
- Entiendo que significa `-p 8080:80`
- Se que archivo define como construir una imagen
- Conozco la diferencia entre `docker rm` y `docker rmi`

## Comandos de apoyo

```bash
# Validar
docker --version
docker info
docker run hello-world

# Nginx de prueba
docker run --name web-demo -d -p 8080:80 nginx
docker ps
docker stop web-demo
docker ps -a
docker rm web-demo
docker images

# App Flask
cd codigo/sesion1
docker build -t mi-flask:v1 .
docker run --name flask-demo -d -p 5000:5000 mi-flask:v1
docker ps
docker logs flask-demo
docker stop flask-demo
docker rm flask-demo
docker rmi mi-flask:v1
```

---

[Siguiente: Dockerfile profesional](./02-dockerfile-profesional.md)
