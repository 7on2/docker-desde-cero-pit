# Prueba 1: Flask sin Docker

Este ejemplo muestra como ejecutar la aplicacion directamente en el sistema operativo, sin contenedores.

## Dependencias del sistema

- Python instalado
- Flask instalado manualmente

## Ejecucion

```bash
# Instalar Flask
pip install flask

# Ejecutar la app
python app.py
```

Abrir `http://localhost:5000`

## Problemas que expone este enfoque

| Problema | Descripcion |
|---|---|
| Python necesario | Cada maquina debe tener Python instalado |
| Flask necesario | Cada maquina debe instalar Flask |
| Versiones distintas | `pip install flask` puede instalar versiones distintas |
| Entorno local | La configuracion de cada equipo afecta la ejecucion |
| No reproducible | Otro alumno sin Flask o con otra version podria tener errores |

Este ejemplo sirve como punto de comparacion para entender por que Docker existe.
