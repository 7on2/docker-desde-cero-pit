# Docker desde Cero: Crea y Despliega Aplicaciones

Repositorio del curso PIT 2026 para aprender Docker desde cero hasta levantar aplicaciones multi-contenedor con Docker Compose, Flask y PostgreSQL. Incluye clases resumidas, laboratorios por sesion, codigo base y material visual del curso.

## Ruta De Aprendizaje

| Sesion | Tema | Clase | Laboratorio |
|---|---|---|---|
| 01 | Contenedores desde cero | [Abrir](./clases/01-contenedores-desde-cero.md) | [Lab 01](./laboratorios/sesion1/README.md) |
| 02 | Dockerfile profesional | [Abrir](./clases/02-dockerfile-profesional.md) | [Lab 02](./laboratorios/sesion2/README.md) |
| 03 | Docker Compose y apps multi-contenedor | [Abrir](./clases/03-docker-compose.md) | [Lab 03](./laboratorios/sesion3/README.md) |
| 04 | Redes, volumenes y persistencia | [Abrir](./clases/04-redes-volumenes-persistencia.md) | [Lab 04](./laboratorios/sesion4/README.md) |
| 05 | Docker en produccion | [Abrir](./clases/05-docker-en-produccion.md) | Por desarrollar |
| 06 | Proyecto final y despliegue completo | [Abrir](./clases/06-proyecto-final.md) | Por desarrollar |

> El indice sigue el temario oficial y los slides actuales. Las sesiones 1 a 4 tienen desarrollo completo en esta version.

## Mapa Rapido

```mermaid
flowchart LR
    S1["S1 Contenedores"] --> S2["S2 Dockerfile"] --> S3["S3 Compose"] --> S4["S4 Redes y volumenes"] --> S5["S5 Produccion"] --> S6["S6 Proyecto final"]
    style S1 fill:#1f6feb,stroke:#58a6ff,color:#fff
    style S2 fill:#238636,stroke:#3fb950,color:#fff
    style S3 fill:#8957e5,stroke:#bc8cff,color:#fff
    style S4 fill:#9e6a03,stroke:#d29922,color:#fff
    style S5 fill:#da3633,stroke:#f85149,color:#fff
    style S6 fill:#30363d,stroke:#8b949e,color:#fff
```

## Laboratorios

| Lab | Objetivo | Codigo |
|---|---|---|
| [Sesion 1](./laboratorios/sesion1/README.md) | Construir y ejecutar una app Flask en contenedor | [codigo/sesion1](./codigo/sesion1/) |
| [Sesion 2](./laboratorios/sesion2/README.md) | Optimizar Dockerfile, usar .dockerignore y tags | [codigo/sesion2](./codigo/sesion2/) |
| [Sesion 3](./laboratorios/sesion3/README.md) | Levantar Flask + PostgreSQL con Compose | [codigo/sesion3](./codigo/sesion3/) |
| [Sesion 4](./laboratorios/sesion4/README.md) | Aislar PostgreSQL, persistir datos y crear backups | [codigo/sesion4](./codigo/sesion4/) |

## Material De Apoyo

| Material | Descripcion |
|---|---|
| [Slides completos](./material/slides-programa-completo-docker.pdf) | Presentacion Beamer del curso. |
| [Fuente LaTeX](./material/programa_completo_docker.tex) | Archivo fuente de los slides. |
| [Temario oficial](./material/temario-docker-desde-cero.pdf) | PDF con objetivos, requisitos y sesiones. |
| [Imagenes](./imagenes/) | Recursos visuales usados por el curso. |
| [Recursos](./recursos/) | Logos y material complementario. |

## Requisitos

- Docker Desktop o Docker Engine instalado.
- Docker Compose disponible como `docker compose`.
- Terminal basica en Windows, Linux o macOS.
- 4 GB de RAM minimo, 8 GB recomendado.
