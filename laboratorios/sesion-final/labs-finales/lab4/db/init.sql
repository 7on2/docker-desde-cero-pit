CREATE TABLE IF NOT EXISTS tareas (
    id         SERIAL PRIMARY KEY,
    titulo     VARCHAR(255) NOT NULL,
    completado BOOLEAN DEFAULT FALSE,
    creado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tareas (titulo) VALUES
    ('Validar healthchecks'),
    ('Ejecutar backup de PostgreSQL'),
    ('Revisar hardening del stack');
