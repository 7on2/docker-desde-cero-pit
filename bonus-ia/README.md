# Bonus: Inteligencia Artificial para Operaciones — Conceptos Fundamentales

Complemento del curso Docker PIT que introduce los conceptos de IA generativa, agentes, tokens, MCP, skills, LLMs y herramientas como Claude y opencode, orientados a profesionales de infraestructura y seguridad.

---

## 1. Large Language Models (LLMs)

### ¿Qué es un LLM?

Un **Large Language Model** es un modelo de inteligencia artificial entrenado sobre billones de textos para predecir cuál es el próximo token más probable dado un contexto. No "entiende" el texto como un humano; calcula probabilidades estadísticas sobre secuencias de tokens.

### ¿Cómo funciona internamente?

1. **Entrada**: El usuario escribe un prompt (texto).
2. **Tokenización**: El texto se divide en tokens (unidades atómicas que pueden ser palabras, subpalabras o caracteres).
3. **Embedding**: Cada token se convierte en un vector numérico de alta dimensionalidad (ej. 4096 dimensiones).
4. **Atención (Transformer)**: El modelo calcula relaciones entre todos los tokens simultáneamente usando el mecanismo de *self-attention*. Cada token "mira" los demás tokens del contexto para determinar su relevancia.
5. **Predicción**: El modelo genera una distribución de probabilidad sobre el vocabulario para el siguiente token. Se selecciona el token más probable (o se muestrea con temperatura).
6. **Decodificación**: El token generado se agrega al contexto y se repite el proceso hasta alcanzar un límite o un token de fin.

### Modelos principales

| Modelo | Desarrollador | Contexto máximo | Características |
|--------|---------------|----------------|-----------------|
| **GPT-4o** | OpenAI | 128K tokens | Multimodal (texto, imagen, audio). Razonamiento avanzado. |
| **Claude 3.5 Sonnet / Opus** | Anthropic | 200K tokens | Alto razonamiento, seguimiento de instrucciones, baja alucinación. |
| **Gemini 1.5 Pro** | Google | 1M+ tokens | Ventana de contexto masiva. Multimodal nativo. |
| **Llama 3** | Meta | 128K tokens | Open-weight. Se puede correr localmente. |
| **Mistral / Mixtral** | Mistral AI | 32K tokens | Eficiente, open-weight. MoE (Mixture of Experts) en Mixtral. |
| **GloM 5** | Zhipu AI | 128K+ tokens | Modelo de razonamiento multi-propósito. |

### Parametros de generación

| Parámetro | Qué controla | Rango típico |
|-----------|-------------|-------------|
| **Temperature** | Aleatoriedad de la salida. 0 = determinista, 1 = creativo | 0.0 – 2.0 |
| **Top-p (nucleus sampling)** | Porcentaje acumulado de tokens probables considerados | 0.1 – 1.0 |
| **Top-k** | Número fijo de tokens más probables considerados | 1 – 100 |
| **Max tokens** | Longitud máxima de la respuesta generada | 1 – contexto máx. |
| **Frequency penalty** | Penaliza tokens ya usados frecuentemente | -2.0 – 2.0 |
| **Presence penalty** | Penaliza tokens que ya aparecieron al menos una vez | -2.0 – 2.0 |

> **Temperatura baja (0–0.3)**: ideal para código, datos técnicos, respuestas factuales.
> **Temperatura alta (0.7–1.5)**: ideal para escritura creativa, lluvia de ideas.

---

## 2. Tokens

### ¿Qué es un token?

Un **token** es la unidad atómica que un LLM procesa. No es exactamente una palabra:

- Palabras comunes → 1 token: `"Docker"` → 1 token
- Palabras raras → múltiples tokens: `"containerización"` → puede ser 2-3 tokens
- Código → muchos tokens: `docker compose up -d` → ~5-7 tokens

### Regla práctica de estimación

| Idioma | Approximación |
|--------|--------------|
| Inglés | 1 token ≈ 4 caracteres ≈ 0.75 palabras |
| Español | 1 token ≈ 3 caracteres ≈ 0.55 palabras (el español usa más tokens por las tildes y ñ) |

### Contexto máximo (context window)

La **ventana de contexto** es el número total de tokens (entrada + salida) que el modelo puede procesar en una sola llamada:

| Modelo | Contexto |
|--------|----------|
| GPT-4o | 128,000 tokens |
| Claude 3.5 Sonnet | 200,000 tokens |
| Gemini 1.5 Pro | 1,000,000+ tokens |

> Si tu prompt + respuesta superan el contexto, el modelo trunca o genera error.

### Costos por tokens

Los proveedores cobran por **tokens procesados**:

- **Input tokens**: los tokens de tu prompt (más baratos).
- **Output tokens**: los tokens de la respuesta generada (más caros, típicamente 2-3x el precio de input).

Ejemplo con Claude 3.5 Sonnet (precios referenciales):

| Tipo | Costo por 1M tokens |
|------|---------------------|
| Input | $3.00 |
| Output | $15.00 |

> Un prompt de 10,000 tokens con una respuesta de 2,000 tokens costaría: (10K × $3/M) + (2K × $15/M) = $0.03 + $0.03 = **$0.06**

### Estrategias para optimizar tokens

1. **Prompts concisos**: Elimina información redundante.
2. **Chunking**: Divide documentos grandes en fragmentos y procesa por partes.
3. **Resumen**: Resume el contexto anterior en vez de repetirlo.
4. **Caching**: Usa caching de prompts (ej. Anthropic prompt caching) para prompts repetitivos.
5. **Modelo más pequeño**: Para tareas simples, usa modelos más baratos (Haiku vs Opus).

---

## 3. Agents (Agentes de IA)

### ¿Qué es un agente de IA?

Un **agente** es un sistema que usa un LLM como "cerebro" para tomar decisiones, ejecutar acciones y resolver problemas de forma autónoma o semi-autónoma. A diferencia de un chatbot que solo responde texto, un agente puede:

- **Leer** archivos del sistema de archivos.
- **Ejecutar** comandos en la terminal.
- **Buscar** información en la web o en bases de datos.
- **Escribir** código y modificar archivos.
- **Orquestar** múltiples herramientas en secuencia para completar una tarea compleja.

### Arquitectura de un agente

```
┌─────────────────────────────────────────────────┐
│                   USUARIO                        │
│              (instrucción / tarea)                │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│               AGENTE (LLM)                       │
│                                                   │
│  1. Recibe la instrucción                        │
│  2. Planifica los pasos necesarios               │
│  3. Decide qué herramienta usar en cada paso     │
│  4. Ejecuta la herramienta                       │
│  5. Observa el resultado                         │
│  6. Repite hasta completar la tarea              │
└──────────┬──────────┬──────────┬────────────────┘
           │          │          │
           ▼          ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Bash     │ │ Read     │ │ Web      │
    │ (shell)  │ │ (archi-  │ │ (fetch   │
    │          │ │  vos)    │ │  URLs)   │
    └──────────┘ └──────────┘ └──────────┘
```

### Ciclo de un agente (ReAct Loop)

La mayoría de agentes siguen el patrón **ReAct** (Reasoning + Acting):

1. **Thought** (Pensamiento): El LLM razona sobre qué hacer.
2. **Action** (Acción): El agente ejecuta una herramienta.
3. **Observation** (Observación): El agente recibe el resultado.
4. **Repetir** hasta completar la tarea o alcanzar un límite.

### Tipos de agentes

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **ReAct** | Razona → actúa → observa → repite | opencode, Claude con herramientas |
| **Plan-and-Execute** | Planifica todos los pasos primero, luego ejecuta | Agentes multi-paso complejos |
| **Reflexion** | Evalúa su propia salida y la mejora iterativamente | Code generation con auto-revisión |
| **Multi-agente** | Varios agentes especializados colaboran | CrewAI, AutoGen, LangGraph |

### Herramientas (Tools)

Las herramientas son funciones que el agente puede invocar. Cada herramienta tiene:

- **Nombre**: identificador único.
- **Descripción**: qué hace, cuándo usarla.
- **Esquema de entrada**: parámetros que acepta (tipos, requeridos/opcionales).
- **Implementación**: el código que se ejecuta.

Ejemplo de herramientas típicas en un agente de programación:

| Herramienta | Función |
|------------|---------|
| `bash` | Ejecutar comandos en la terminal |
| `read` | Leer archivos del filesystem |
| `write` | Escribir/crear archivos |
| `edit` | Editar archivos con búsqueda y reemplazo |
| `grep` | Buscar contenido en archivos |
| `glob` | Encontrar archivos por patrón |
| `web_fetch` | Obtener contenido de URLs |

---

## 4. MCP (Model Context Protocol)

### ¿Qué es MCP?

El **Model Context Protocol** es un protocolo abierto creado por Anthropic que estandariza cómo los LLMs se conectan con fuentes de datos y herramientas externas. Es como un "USB-C para la IA": un conector universal.

### ¿Por qué existe?

Antes de MCP, cada herramienta de IA tenía su propia forma de conectarse a bases de datos, APIs y sistemas de archivos. MCP estandariza esto para que:

- Un servidor MCP expone capacidades (herramientas, recursos, prompts).
- Cualquier cliente MCP (como Claude Desktop, opencode, Cursor) puede descubrir y usar esas capacidades automáticamente.
- No necesitas escribir integraciones custom para cada modelo.

### Arquitectura MCP

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   CLIENTE    │  stdio  │   SERVIDOR   │   API   │   FUENTE     │
│  (opencode,  │ ◄─────► │    MCP       │ ◄─────► │  DE DATOS    │
│   Claude)    │  o HTTP │  (middleware)│         │  (BD, APIs,  │
│              │         │              │         │   archivos)  │
└──────────────┘         └──────────────┘         └──────────────┘
```

### Componentes de MCP

| Componente | Descripción |
|-----------|-------------|
| **Resources** | Datos contexuales que el servidor expone al LLM (archivos, esquemas de BD, documentación). Similar a GET en REST. |
| **Tools** | Funciones que el LLM puede invocar para realizar acciones (crear archivo, ejecutar query, enviar notificación). Similar a POST en REST. |
| **Prompts** | Templates de prompts predefinidos que el servidor ofrece al cliente. |

### Ejemplo: Servidor MCP de archivos

Un servidor MCP de filesystem expone herramientas como:

- `read_file(path)` → lee un archivo
- `write_file(path, content)` → escribe un archivo
- `list_directory(path)` → lista directorios
- `search_files(pattern)` → busca archivos por patrón

El cliente (opencode) descubre estas herramientas automáticamente y el LLM decide cuándo usarlas.

### Ejemplo: Servidor MCP de PostgreSQL

Expone recursos (esquemas de tablas) y herramientas (ejecutar queries):

- Resource: `postgres://schemas/tareas_db` → devuelve el esquema de la BD
- Tool: `query(sql)` → ejecuta una query SQL de solo lectura
- Tool: `insert(table, data)` → inserta registros con validación

### MCP en la práctica

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost:5432/db"]
    }
  }
}
```

> MCP permite conectar cualquier fuente de datos sin cambiar el código del agente. Solo se configura el servidor y el cliente lo descubre.

---

## 5. Skills

### ¿Qué son las Skills?

En el contexto de herramientas como opencode, una **skill** es un conjunto de instrucciones especializadas que se inyectan en el contexto del agente cuando detecta que la tarea coincide con un patrón específico. Es como un "modo experto" que el agente activa automáticamente.

### ¿Cómo funcionan?

1. **Disponibilidad**: Las skills se definen en archivos de configuración (`.opencode/skills/`).
2. **Activación**: Cuando el usuario describe una tarea que coincide con la descripción de una skill, el agente carga automáticamente las instrucciones especializadas.
3. **Ejecución**: El agente sigue las instrucciones de la skill para completar la tarea con mayor precisión.

### Ejemplo: Skill de Beamer para Cursos PIT

```markdown
---
name: Beamer Cursos PIT
description: Crear presentaciones LaTeX Beamer con branding institucional OTI
trigger: beamer, presentacion, slides, .tex, curso PIT
---

## Instrucciones

1. Usar el tema UU con colores OTIred.
2. Incluir logo UNI en la esquina.
3. Crear slides obligatorios: portada, objetivos, contenido, resumen.
4. Usar TikZ para diagramas visuales.
5. Compilar con XeLaTeX.
```

Cuando el usuario pide "crear una presentación Beamer", opencode carga esta skill y sigue las instrucciones especializadas en vez de generar código Beamer genérico.

### Skills vs Tools vs Prompts

| Concepto | Qué es | Cuándo se usa |
|----------|--------|---------------|
| **Tool** | Función ejecutable (bash, read, write) | Cuando el agente necesita interactuar con el mundo |
| **Skill** | Instrucciones especializadas inyectadas en contexto | Cuando la tarea requiere conocimiento de dominio |
| **Prompt** | Instrucción directa del usuario | Cuando el usuario guía explícitamente al agente |

> Las skills son **contexto**. Las tools son **acciones**. Los prompts son **instrucciones del usuario**.

---

## 6. Claude

### ¿Qué es Claude?

**Claude** es la familia de modelos de lenguaje de Anthropic. Está diseñada con un enfoque en seguridad, honestidad y útilidad (Constitutional AI).

### Modelos disponibles

| Modelo | Contexto | Fortalezas | Costo relativo |
|--------|----------|------------|----------------|
| **Claude 3.5 Haiku** | 200K | Rápido, económico. Ideal para tareas simples y clasificación. | $ |
| **Claude 3.5 Sonnet** | 200K | Equilibrio entre velocidad y razonamiento. El más versátil. | $$ |
| **Claude 3 Opus** | 200K | Máximo razonamiento y comprensión. Para tareas complejas. | $$$$ |

### Características clave

- **Ventana de contexto de 200K tokens**: ~150,000 palabras, suficiente para documentos largos, código extenso o logs completos.
- **Prompt caching**: Reduce costos hasta 90% reutilizando partes del prompt que no cambian.
- **Vision (multimodal)**: Analiza imágenes, diagramas, capturas de pantalla.
- **Tool use (function calling)**: Puede invocar herramientas externas de forma estructurada.
- **Constitutional AI**: Entrenado para ser honesto, inofensivo y útil. Rechaza solicitudes dañinas y admite cuando no sabe algo.

### Uso a través de la API

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-...")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explica el modelo de capas de Docker en 3 puntos"}
    ]
)
print(message.content[0].text)
```

### Claude con herramientas (Tool Use)

```python
tools = [
    {
        "name": "docker_ps",
        "description": "Lista contenedores Docker en ejecución",
        "input_schema": {
            "type": "object",
            "properties": {
                "all": {"type": "boolean", "description": "Incluir contenedores detenidos"}
            }
        }
    }
]

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "¿Qué contenedores están corriendo?"}
    ]
)
```

Claude responderá con un `tool_use` block solicitando ejecutar `docker_ps`, y tú ejecutas la herramienta y le devuelves el resultado.

---

## 7. opencode

### ¿Qué es opencode?

**opencode** es un agente de IA de código abierto para la terminal que ayuda a tareas de ingeniería de software. Usa LLMs (como Claude, GPT-4, etc.) como motor de razonamiento y tiene acceso a herramientas de filesystem, terminal, búsqueda web y más.

### Características principales

| Característica | Descripción |
|---------------|-------------|
| **Modo terminal** | Interfaz TUI interactiva en la terminal. No requiere IDE. |
| **Multi-modelo** | Soporta Claude, GPT-4, Gemini, Llama y otros vía proveedores configurables. |
| **Herramientas nativas** | bash, read, write, edit, grep, glob, web_fetch y más. |
| **Skills** | Instrucciones especializadas que se activan por contexto (ej. Beamer, Docker, LaTeX). |
| **MCP** | Se conecta a servidores MCP para extender capacidades (BD, APIs, Obsidian, etc.). |
| **Subagents** | Puede lanzar agentes secundarios especializados (explore, general) para tareas en paralelo. |
| **Todo tracking** | Sistema de seguimiento de tareas integrado. |
| **Git integrado** |Lee status, diff, log y gestiona commits/pushes. |

### Flujo de trabajo típico con opencode

```
1. Usuario describe tarea: "Crea un Dockerfile para esta app Flask"
2. opencode analiza el proyecto (lee package.json, requirements.txt, etc.)
3. Genera el Dockerfile siguiendo buenas prácticas
4. Lo escribe en el filesystem
5. Ejecuta docker build para verificar
6. Si hay errores, los lee y corrige
7. Hace commit de los cambios (si el usuario lo solicita)
```

### Configuración de opencode

opencode se configura en `.opencode/config.json` o `opencode.json`:

```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]
    }
  }
}
```

### Skills en opencode

Las skills se definen en `.opencode/skills/`:

```
.opencode/
  skills/
    beamer-cursos-pit/
      SKILL.md       ← Instrucciones especializadas
    docker-hardening/
      SKILL.md       ← Hardening de contenedores Docker
```

Cuando el usuario pide algo relacionado con Beamer, opencode carga automáticamente la skill y sigue las instrucciones del `SKILL.md`.

### Subagentes

opencode puede lanzar agentes secundarios:

| Tipo | Especialidad |
|------|-------------|
| **explore** | Búsqueda rápida de archivos, patrones, preguntas sobre el código |
| **general** | Tareas multi-paso complejas con múltiples ejecuciones en paralelo |

---

## 8. Integración de Conceptos: Flujo Completo

### Escenario: Usar IA para diagnosticar un contenedor Docker

```
Usuario: "Mi contenedor tareas-app falla al iniciar, ayúdame a diagnosticar"

Agente (opencode):
  1. [Thought] Necesito ver los logs del contenedor y su estado.
  2. [Action] bash: docker ps -a | grep tareas-app
  3. [Observation] CONTAINER ID  STATUS         NAMES
                   abc123        Exited (1) 5m  tareas-app
  4. [Action] bash: docker logs tareas-app --tail 50
  5. [Observation] psycopg2.OperationalError: could not connect to server: Connection refused
  6. [Thought] La app no puede conectar a PostgreSQL. Verifico si la BD está corriendo.
  7. [Action] bash: docker ps | grep tareas-db
  8. [Observation] No output (la BD no está corrienda)
  9. [Thought] La BD está detenida. Verifico el healthcheck y los logs.
  10. [Action] bash: docker compose -f docker-compose.prod.yml ps
  11. [Observation] tareas-db: Exited (137) 10 minutes ago
  12. [Thought] La BD fue killed (OOM probable). Verifico límites de memoria.
  13. [Action] bash: docker inspect tareas-db --format '{{.HostConfig.Memory}}'
  14. [Observation] 268435456 (256MB)
  15. [Thought] 256MB puede ser insuficiente para PostgreSQL con datos grandes.
  
  Respuesta al usuario:
  "El contenedor tareas-app falla porque tareas-db fue killed (código 137 = OOM).
   PostgreSQL tiene un límite de 256MB que puede ser insuficiente.
   
   Solución: Aumenta el límite de memoria en docker-compose.prod.yml:
   
   db:
     deploy:
       resources:
         limits:
           memory: 512M    ← cambiar de 256M a 512M
   
   Luego: docker compose -f docker-compose.prod.yml up -d --force-recreate db"
```

### Escenario: Generar un Dockerfile con agente IA

```
Usuario: "Genera un Dockerfile de producción para mi app Flask"

Agente:
  1. [Read] Lee requirements.txt → identifica Flask, psycopg2, gunicorn
  2. [Read] Lee app.py → identifica el puerto 5000, endpoints /health
  3. [Read] Lee .env.example → identifica variables de entorno
  4. [Write] Genera Dockerfile con:
     - FROM python:3.11-slim
     - USER appuser (no-root)
     - HEALTHCHECK
     - Multi-stage build
     - .dockerignore
  5. [Bash] Ejecuta docker build -t app:test .
  6. [Observation] Build exitoso. Tamaño: 180MB
  7. [Bash] Ejecuta docker build -f Dockerfile.multistage -t app:slim .
  8. [Observation] Build exitoso. Tamaño: 85MB (53% reducción)
  
  Resultado: Dockerfile + Dockerfile.multistage + .dockerignore optimizados
```

---

## 9. Conceptos Clave — Resumen Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA DE IA PARA DEVOPS                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │   LLMs   │    │  TOKENS  │    │ AGENTS   │                  │
│  │          │    │          │    │          │                  │
│  │ GPT-4o   │    │ Unidad   │    │ Auto-    │                  │
│  │ Claude   │◄──►│ atómica  │◄──►│ nomonos  │                  │
│  │ Gemini   │    │ del modelo│    │ con      │                  │
│  │ Llama    │    │          │    │ tools    │                  │
│  └──────────┘    └──────────┘    └────┬─────┘                  │
│                                         │                        │
│                    ┌────────────────────┼───────────────────┐   │
│                    │                    │                   │   │
│                    ▼                    ▼                   ▼   │
│             ┌──────────┐    ┌──────────────┐    ┌──────────┐ │
│             │   MCP    │    │   SKILLS     │    │ OPENCODE │ │
│             │          │    │              │    │          │ │
│             │ Protocolo│    │ Instruc-     │    │ Agente   │ │
│             │ universal│    │ ciones       │    │ terminal │ │
│             │ para      │    │ especial-   │    │ con      │ │
│             │ conectar  │    │ izadas      │    │ tools,   │ │
│             │ datos     │    │ por dominio │    │ skills,  │ │
│             │ externos  │    │             │    │ MCP      │ │
│             └──────────┘    └──────────────┘    └──────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Comparativa de Conceptos

| Concepto | Analogía | Qué hace | Ejemplo concreto |
|----------|----------|----------|-----------------|
| **LLM** | Cerebro | Procesa lenguaje y genera texto | Claude 3.5 Sonnet leyendo logs de Docker |
| **Token** | Letra/palabra | Unidad de procesamiento del LLM | `"Docker"` = 1 token, `"containerización"` = 3 tokens |
| **Agent** | Empleado autónomo | Toma decisiones y ejecuta acciones | opencode diagnosticando un contenedor que falla |
| **Tool** | Herramienta del empleado | Función ejecutable que el agente invoca | `bash` para ejecutar `docker logs` |
| **MCP** | enchufe USB-C | Protocolo estándar para conectar fuentes de datos | Servidor MCP de PostgreSQL conectado a Claude |
| **Skill** | Manual de procedimiento | Instrucciones especializadas por dominio | Skill de Beamer que aplica branding OTI automáticamente |
| **Context window** | Memoria a corto plazo | Espacio total de tokens (entrada + salida) | 200K tokens en Claude 3.5 |
| **Temperature** | Nivel de creatividad | Controla aleatoriedad de la respuesta | 0.0 para código, 0.7 para prosa |
| **Prompt** | Orden del jefe | Instrucción que el usuario da al modelo | "Crea un Dockerfile de producción para Flask" |

---

## 11. Recursos

| Recurso | Enlace |
|---------|--------|
| Documentación de Anthropic | https://docs.anthropic.com |
| Model Context Protocol (MCP) | https://modelcontextprotocol.io |
| opencode (GitHub) | https://github.com/anomalyco/opencode |
| Claude API | https://console.anthropic.com |
| Especificación de tokens | https://docs.anthropic.com/en/docs/build-with-claude/tokenizer |
| Prompt caching | https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching |

---

*Universidad Nacional de Ingeniería — OTI-UNI SOC · Lima, Perú*