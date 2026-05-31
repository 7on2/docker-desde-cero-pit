# Fundamentos de Docker — Sesión 05: Datos y Redes

> **Instructor:** Anthony Gonzalo Quispe Cordova  
> **Fecha:** 21 de febrero de 2026  
> **Programa:** PIT 2026 — Universidad Nacional de Ingeniería

---

## Contenido

1. [Almacenamiento y Gestión de Datos en Docker](#1-almacenamiento-y-gestión-de-datos-en-docker)
2. [Redes en Docker (Docker Networks)](#2-redes-en-docker-docker-networks)

---

# 1. Almacenamiento y Gestión de Datos en Docker

> Bind Mounts, Volúmenes y Docker CP

---

## Definiciones: Bind Mount y Volumen

### Bind Mount (Montaje Directo)

Un **Bind Mount** permite montar un directorio de tu PC directamente dentro de un contenedor. No se hace una copia: el contenedor accede a los mismos archivos que tienes en tu sistema. Cualquier cambio en uno se refleja en el otro al instante.

### Volumen (Volume)

Un **Volumen** es un espacio de almacenamiento administrado por Docker. A diferencia del bind mount, Docker controla en dónde se guardan los datos en el host. Son ideales para datos que necesitan persistir aunque el contenedor se elimine (bases de datos, archivos generados, etc).

### Sintaxis

```bash
--volume <ruta_local>:<ruta_contenedor>   # Bind Mount
--volume <ruta_contenedor>                # Volumen
```

---

## Ejercicio: Nuestra App de Práctica

### El proyecto: `mi-app`

Usaremos una app web sencilla hecha con **Node.js + Express**. Tiene un servidor que muestra una página HTML en el puerto 3000.

```
mi-app/
  app.js          # Servidor Express
  package.json    # Dependencias (express, nodemon)
  Dockerfile      # Para construir la imagen
```

Construir la imagen Docker:

```bash
cd mi-app
docker build -t mi-app-demo .
```

> Ya tenemos nuestra imagen `mi-app-demo` lista. Ahora veamos qué pasa **sin** y **con** Bind Mount.

---

## Parte 1: SIN Bind Mount

> Los datos dentro del contenedor se pierden al eliminarlo.

### Objetivo

Demostrar que todo lo creado dentro de un contenedor desaparece al eliminarlo.

```bash
# Paso 1: Correr el contenedor en modo interactivo
docker run -it --rm --name sin-mount mi-app-demo bash
```

| Flag | Descripción |
|------|-------------|
| `-it` | Modo interactivo (terminal dentro del contenedor) |
| `--rm` | El contenedor se elimina al salir |
| `bash` | Abrimos una shell dentro del contenedor |

```bash
# Paso 2: Crear un archivo DENTRO del contenedor
root@abc123:/app# echo "Archivo importante" > archivo-secreto.txt
root@abc123:/app# cat archivo-secreto.txt
Archivo importante
```

```bash
# Paso 3: Modificar app.js dentro del contenedor
root@abc123:/app# sed -i 's/Bind Mount Activo/CAMBIO TEMPORAL/' app.js
root@abc123:/app# grep "badge" app.js
<div class="badge">CAMBIO TEMPORAL</div>
```

```bash
# Paso 4: Salir del contenedor
root@abc123:/app# exit
```

> ⚠️ Al salir, el contenedor se destruye (por `--rm`). **Todo lo que hicimos dentro del contenedor desaparece:**
> - El `archivo-secreto.txt` que creamos: **NO existe en tu PC**.
> - El cambio en `app.js`: **NO se refleja en tu PC**.

### Verificar que todo se perdió

```bash
# En tu PC: verificar que los cambios NO existen
$ cat mi-app/archivo-secreto.txt
cat: mi-app/archivo-secreto.txt: No such file or directory

$ grep "badge" mi-app/app.js
<div class="badge">Bind Mount Activo</div>
```

```
{ } Tu PC (Intacta)  ---COPIED--->  { } Contenedor (Copia aislada)
                                          exit → Todo se pierde
```

---

## Parte 2: CON Bind Mount

> Los datos persisten porque viven en tu PC.

### La clave: `-v`

Ahora montamos nuestra carpeta local directamente dentro del contenedor. Usamos la imagen oficial `node:18`.

```bash
# Paso 1: Correr con Bind Mount
docker run -it --rm \
  --name con-mount \
  -v "$(pwd)":/app \
  -w /app \
  node:18 bash
```

| Flag | Descripción |
|------|-------------|
| `-v "$(pwd)":/app` | Monta TU carpeta actual dentro del contenedor en `/app` |
| `-w /app` | Establece `/app` como directorio de trabajo |
| `node:18` | Usamos imagen oficial (no necesitamos imagen propia) |

```bash
# Paso 2: Instalar dependencias y crear un archivo
root@xyz789:/app# npm install
root@xyz789:/app# echo "Archivo con Bind Mount" > archivo-persistente.txt
root@xyz789:/app# cat archivo-persistente.txt
Archivo con Bind Mount
```

```bash
# Paso 3: Modificar app.js dentro del contenedor
root@xyz789:/app# sed -i 's/Bind Mount Activo/MODIFICADO DESDE CONTENEDOR/' app.js
root@xyz789:/app# grep "badge" app.js
<div class="badge">MODIFICADO DESDE CONTENEDOR</div>
```

```bash
# Paso 4: Salir del contenedor
root@xyz789:/app# exit
```

### Verificar — Todo persiste

```bash
# En tu PC: los archivos SIGUEN existiendo
$ cat archivo-persistente.txt
Archivo con Bind Mount

$ grep "badge" app.js
<div class="badge">MODIFICADO DESDE CONTENEDOR</div>
```

```
{ } Tu PC (Persiste)  <===MISMO ARCHIVO===>  Contenedor (Referenciado)
```

---

## Tabla Resumen: Sin vs Con Bind Mount

| Situación | Sin Bind Mount | Con Bind Mount |
|-----------|---------------|----------------|
| Archivo creado dentro | Se pierde al salir | Se guarda en tu PC |
| Editas código en tu PC | El contenedor no lo ve | Lo ve al instante |
| El contenedor se elimina | Todo desaparece | Tu código sigue intacto |
| Nuevo contenedor | Empieza desde cero | Accede a tus archivos |
| Ideal para... | Producción | Desarrollo local |

---

## `docker cp`: Copiar archivos sin montar

### ¿Y si solo necesito pasar un archivo rápido?

Con `docker cp` podemos copiar archivos entre nuestra PC y un contenedor **sin necesidad de configurar bind mounts**. Funciona en ambas direcciones.

- Funciona aunque el contenedor esté **detenido**.
- Útil para extraer logs, configs o resultados rápidamente.

```bash
# Sacar un archivo del contenedor a tu PC
docker cp hello-dock-dev:/home/node/app/package.json .

# Meter un archivo de tu PC al contenedor
docker cp mi_config.json hello-dock-dev:/home/node/app/
```

---

# 2. Redes en Docker (Docker Networks)

> Comunicación entre contenedores y el mundo exterior

---

## Definiciones: Docker Networking

**Docker Networking** es el sistema que permite a los contenedores comunicarse entre sí, con el host, y con el mundo exterior. Docker administra automáticamente las interfaces de red, direcciones IP y reglas de enrutamiento de cada contenedor.

| Driver | Descripción |
|--------|-------------|
| `bridge` | Red privada interna (por defecto). Contenedores se comunican entre sí. |
| `host` | Sin aislamiento: el contenedor comparte la red de tu PC. |
| `none` | Sin red alguna. Contenedor 100% aislado. |
| `overlay` | Conecta contenedores entre varias computadoras (clusters). |

---

## Las redes que ya tienes instaladas

Al instalar Docker, ya existen **tres redes preconfiguradas**. Todo contenedor que levantes se conecta automáticamente a `bridge`.

```bash
docker network ls
# NETWORK ID     NAME      DRIVER    SCOPE
# c2e59f2b96bd   bridge    bridge    local
# 124dccee067f   host      host      local
# 506e3822bf1f   none      null      local
```

| Red | Descripción |
|-----|-------------|
| `bridge` | Red por defecto. Cada contenedor recibe IP privada (`172.17.0.x`). |
| `host` | Comparte la IP de tu PC sin aislamiento. |
| `none` | Sin red (aislado totalmente). |

---

## El problema: Conectar 2 contenedores

### Escenario real

Tenemos una **API (Node/Express)** y una **base de datos (PostgreSQL)** corriendo en contenedores separados. Necesitan comunicarse.

### Intentos que NO funcionan bien

- Usar `127.0.0.1` desde la API → **NO funciona**. Cada contenedor tiene su propio localhost aislado.
- Buscar la IP con `inspect` → Funciona, pero si el contenedor se destruye y recrea, la IP cambia. No es confiable.

```bash
# Buscar IP manualmente (NO recomendado)
docker inspect --format='{{ range .NetworkSettings.Networks }}{{.IPAddress}}{{ end }}' mi_postgres
# 172.17.0.2
```

---

## La solución: Redes definidas por el usuario

### User-Defined Bridge Network

La solución correcta es **crear una red propia** y conectar ambos contenedores a ella.

**Ventajas:**
- **DNS automático:** Los contenedores se encuentran por nombre (ej. `ping mi_db`) sin necesidad de saber la IP.
- **Mejor aislamiento:** Solo los contenedores que tú conectes pueden comunicarse.
- **Conexión en caliente:** Puedes agregar o quitar contenedores de la red sin detenerlos.

```bash
# Crear una red personalizada
docker network create mi_red

# Verificar que fue creada
docker network ls
# NETWORK ID     NAME      DRIVER    SCOPE
# be0cab667c4b   bridge    bridge    local
# 124dccee067f   host      host      local
# 506e3822bf1f   none      null      local
# 7bd5f351aa89   mi_red    bridge    local
```

---

## Conectar contenedores a la red

Hay **dos formas** de conectar un contenedor a una red:

```bash
# Forma 1: Al crear el contenedor
docker run -d --network mi_red --name servidor nginx
```

```bash
# Forma 2: Conectar un contenedor existente (en caliente)
docker network connect mi_red mi_contenedor
```

```bash
# Verificar qué contenedores están en la red
docker network inspect --format=\
'{{ range .Containers }}{{.Name}} {{ end }}' mi_red
# servidor mi_contenedor
```

---

## Ejercicio: Probar comunicación con ping

### Objetivo

Demostrar que dos contenedores en la misma red se encuentran **por nombre** gracias al DNS automático.

```bash
# 1. Crear la red
docker network create red_prueba

# 2. Levantar un servidor web en esa red
docker run -d --network red_prueba --name web nginx

# 3. Levantar Alpine y hacer ping al servidor por nombre
docker run -it --rm --network red_prueba alpine sh
/ # ping web
PING web (172.18.0.2): 56 data bytes
64 bytes from 172.18.0.2: seq=0 ttl=64 time=0.19 ms
64 bytes from 172.18.0.2: seq=1 ttl=64 time=0.10 ms
```

> ✅ Funciona: Alpine encuentra a `web` por nombre **sin necesidad de saber su IP**.

---

## Desconectar y eliminar redes

```bash
# Desconectar un contenedor de la red
docker network disconnect red_prueba web

# Eliminar una red específica
docker network rm red_prueba

# Eliminar TODAS las redes sin usar
docker network prune
```

> ⚠️ **Importante:**
> - No puedes eliminar una red si tiene contenedores conectados.
> - Para que el DNS automático funcione, debes asignar nombre a los contenedores (con `--name`).

---

## Mapeo de Puertos: Acceder desde el navegador

### El problema

Los servicios dentro de una red Docker son **internos**. Para que tu navegador los vea, debes mapear puertos con `-p`.

| Flag | Descripción |
|------|-------------|
| `-p 8080:80` | Puerto 8080 de tu PC redirige al 80 del contenedor |
| `-P` (mayúscula) | Docker elige un puerto aleatorio |

```bash
# Mapear puerto 8080 de mi PC al 80 del contenedor
docker run -d -p 8080:80 --name mi_web nginx

# Abrir en el navegador: http://localhost:8080

# Ver puertos mapeados
docker port mi_web
# 80/tcp -> 0.0.0.0:8080
```

---

## Resumen de Comandos

### Almacenamiento

| Comando | Descripción |
|---------|-------------|
| `-v "$(pwd)":/app` | Bind Mount (carpeta local → contenedor) |
| `-v /app` | Volumen gestionado por Docker |
| `docker cp origen destino` | Copiar archivos entre PC y contenedor |

### Redes

| Comando | Descripción |
|---------|-------------|
| `docker network ls` | Listar todas las redes |
| `docker network create <nombre>` | Crear red personalizada |
| `docker network connect <red> <contenedor>` | Conectar contenedor a red |
| `docker network disconnect <red> <contenedor>` | Desconectar contenedor de red |
| `docker network inspect <nombre>` | Inspeccionar detalles de la red |
| `docker network rm <nombre>` | Eliminar una red |
| `docker network prune` | Eliminar todas las redes sin usar |
| `-p 8080:80` | Mapear puerto del host al contenedor |
