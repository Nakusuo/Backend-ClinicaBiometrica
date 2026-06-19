CREATE TABLE doctores (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    especialidad VARCHAR(100),
    password_hash TEXT,
    embedding_facial TEXT,
    rol VARCHAR(20) DEFAULT 'doctor',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) UNIQUE,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    fecha_nacimiento DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE expedientes (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    historial TEXT,
    diagnostico TEXT,
    tratamiento TEXT,
    notas TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    doctor_id INTEGER REFERENCES doctores(id),
    fecha TIMESTAMP,
    estado VARCHAR(30),
    motivo TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';