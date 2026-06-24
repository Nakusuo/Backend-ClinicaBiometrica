-- =========================================================
-- TELEMEDICINA INTEGRADA - POSTGRESQL
-- VERSIÓN CORREGIDA PARA FASTAPI + ANGULAR + WEBRTC
-- =========================================================

-- =========================================================
-- ELIMINAR OBJETOS EXISTENTES
-- =========================================================

DROP VIEW IF EXISTS vista_historial_completo CASCADE;

DROP TABLE IF EXISTS llamadas CASCADE;
DROP TABLE IF EXISTS examenes CASCADE;
DROP TABLE IF EXISTS recetas CASCADE;
DROP TABLE IF EXISTS consultas CASCADE;
DROP TABLE IF EXISTS citas CASCADE;
DROP TABLE IF EXISTS expedientes CASCADE;
DROP TABLE IF EXISTS pacientes CASCADE;
DROP TABLE IF EXISTS doctores CASCADE;

-- =========================================================
-- DOCTORES
-- =========================================================

CREATE TABLE doctores (
    id SERIAL PRIMARY KEY,

    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,

    correo VARCHAR(100) UNIQUE NOT NULL,
    especialidad VARCHAR(100),

    cedula VARCHAR(50),
    telefono VARCHAR(50),

    password_hash TEXT,
    embedding_facial TEXT,

    rol VARCHAR(20) DEFAULT 'doctor',

    activo BOOLEAN DEFAULT TRUE,

    ultimo_login TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- PACIENTES
-- =========================================================

CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,

    dni VARCHAR(20) UNIQUE NOT NULL,

    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,

    telefono VARCHAR(20),
    correo VARCHAR(100),

    fecha_nacimiento DATE,

    direccion TEXT,

    genero VARCHAR(10),

    password_hash TEXT,
    embedding_facial TEXT,

    ultimo_login TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- EXPEDIENTES
-- =========================================================

CREATE TABLE expedientes (
    id SERIAL PRIMARY KEY,

    paciente_id INTEGER NOT NULL UNIQUE,

    alergias_conocidas TEXT,
    padecimientos_cronicos TEXT,

    grupo_sanguineo VARCHAR(5),
    factor_rh VARCHAR(2),

    historial_resumido TEXT,

    antecedentes_familiares TEXT,
    antecedentes_quirurgicos TEXT,

    habitos_salud TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_expediente_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES pacientes(id)
        ON DELETE CASCADE
);

-- =========================================================
-- CITAS
-- =========================================================

CREATE TABLE citas (
    id SERIAL PRIMARY KEY,

    paciente_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,

    fecha TIMESTAMP NOT NULL,

    estado VARCHAR(30) DEFAULT 'pendiente',

    motivo TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cita_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES pacientes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cita_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctores(id)
        ON DELETE CASCADE
);

-- =========================================================
-- CONSULTAS
-- =========================================================

CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,

    expediente_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,

    cita_id INTEGER,

    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    motivo_consulta TEXT,
    sintomas TEXT,

    signos_vitales JSONB,

    diagnostico_principal TEXT,
    diagnostico_diferencial TEXT,

    notas_doctor TEXT,

    tipo_consulta VARCHAR(30),

    estado VARCHAR(20) DEFAULT 'activa',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_consulta_expediente
        FOREIGN KEY (expediente_id)
        REFERENCES expedientes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_consulta_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctores(id),

    CONSTRAINT fk_consulta_cita
        FOREIGN KEY (cita_id)
        REFERENCES citas(id)
        ON DELETE SET NULL
);

-- =========================================================
-- RECETAS
-- =========================================================

CREATE TABLE recetas (
    id SERIAL PRIMARY KEY,

    consulta_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,

    nombre_medicamento VARCHAR(150) NOT NULL,

    concentracion VARCHAR(50),
    presentacion VARCHAR(50),

    dosis VARCHAR(100),
    frecuencia VARCHAR(100),

    duracion_tratamiento VARCHAR(50),

    indicaciones_especiales TEXT,

    fecha_receta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    activo BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_receta_consulta
        FOREIGN KEY (consulta_id)
        REFERENCES consultas(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_receta_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES pacientes(id),

    CONSTRAINT fk_receta_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctores(id)
);

-- =========================================================
-- EXAMENES
-- =========================================================

CREATE TABLE examenes (
    id SERIAL PRIMARY KEY,

    consulta_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL,
    doctor_solicitante_id INTEGER NOT NULL,

    tipo_examen VARCHAR(50),

    nombre_examen VARCHAR(150) NOT NULL,

    categoria VARCHAR(50),

    resultado TEXT,

    archivo_url VARCHAR(255),

    es_imagen BOOLEAN DEFAULT FALSE,

    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_resultado TIMESTAMP,

    estado VARCHAR(20) DEFAULT 'pendiente',

    notas_doctor TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_examen_consulta
        FOREIGN KEY (consulta_id)
        REFERENCES consultas(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_examen_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES pacientes(id),

    CONSTRAINT fk_examen_doctor
        FOREIGN KEY (doctor_solicitante_id)
        REFERENCES doctores(id)
);

-- =========================================================
-- LLAMADAS WEBRTC
-- =========================================================

CREATE TABLE llamadas (
    id SERIAL PRIMARY KEY,

    cita_id INTEGER NOT NULL,

    paciente_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,

    room_id VARCHAR(100) UNIQUE NOT NULL,

    token_sesion TEXT,

    estado VARCHAR(20) DEFAULT 'esperando',

    start_time TIMESTAMP,
    end_time TIMESTAMP,

    duracion INTEGER,

    grabacion_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_llamada_cita
        FOREIGN KEY (cita_id)
        REFERENCES citas(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_llamada_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES pacientes(id),

    CONSTRAINT fk_llamada_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctores(id)
);

-- =========================================================
-- INDICES
-- =========================================================

CREATE INDEX idx_doctores_correo
ON doctores(correo);

CREATE INDEX idx_pacientes_dni
ON pacientes(dni);

CREATE INDEX idx_pacientes_correo
ON pacientes(correo);

CREATE INDEX idx_expedientes_paciente
ON expedientes(paciente_id);

CREATE INDEX idx_citas_paciente
ON citas(paciente_id);

CREATE INDEX idx_citas_doctor
ON citas(doctor_id);

CREATE INDEX idx_citas_fecha
ON citas(fecha);

CREATE INDEX idx_consultas_expediente
ON consultas(expediente_id);

CREATE INDEX idx_consultas_fecha
ON consultas(fecha_consulta);

CREATE INDEX idx_recetas_paciente
ON recetas(paciente_id);

CREATE INDEX idx_recetas_consulta
ON recetas(consulta_id);

CREATE INDEX idx_examenes_paciente
ON examenes(paciente_id);

CREATE INDEX idx_examenes_consulta
ON examenes(consulta_id);

CREATE INDEX idx_llamadas_room
ON llamadas(room_id);

-- =========================================================
-- VISTA HISTORIAL CLINICO
-- =========================================================

CREATE OR REPLACE VIEW vista_historial_completo AS
SELECT
    p.id AS paciente_id,
    p.dni,
    p.nombres || ' ' || p.apellidos AS nombre_completo,
    p.fecha_nacimiento,
    p.telefono,
    p.correo,

    e.alergias_conocidas,
    e.padecimientos_cronicos,
    e.grupo_sanguineo,
    e.factor_rh,
    e.historial_resumido,
    e.antecedentes_familiares,
    e.antecedentes_quirurgicos,

    (
        SELECT jsonb_build_object(
            'fecha', c.fecha_consulta,
            'diagnostico', c.diagnostico_principal,
            'doctor', d.nombres || ' ' || d.apellidos,
            'motivo', c.motivo_consulta
        )
        FROM consultas c
        LEFT JOIN doctores d ON d.id = c.doctor_id
        WHERE c.expediente_id = e.id
        ORDER BY c.fecha_consulta DESC
        LIMIT 1
    ) AS ultima_consulta,

    (
        SELECT COUNT(*)
        FROM consultas c
        WHERE c.expediente_id = e.id
    ) AS total_consultas,

    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'medicamento', r.nombre_medicamento,
                'dosis', r.dosis,
                'frecuencia', r.frecuencia
            )
        )
        FROM recetas r
        WHERE r.paciente_id = p.id
        AND r.activo = TRUE
    ) AS medicamentos_activos,

    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'examen', ex.nombre_examen,
                'tipo', ex.tipo_examen,
                'fecha', ex.fecha_solicitud,
                'resultado', ex.resultado
            )
        )
        FROM (
            SELECT *
            FROM examenes
            WHERE paciente_id = p.id
            ORDER BY fecha_solicitud DESC
            LIMIT 5
        ) ex
    ) AS ultimos_examenes

FROM pacientes p
LEFT JOIN expedientes e
ON p.id = e.paciente_id;

-- =========================================================
-- DATOS INICIALES
-- =========================================================

INSERT INTO doctores (
    nombres,
    apellidos,
    correo,
    especialidad,
    rol
)
VALUES (
    'Administrador',
    'Sistema',
    'admin@telemedicina.com',
    'General',
    'admin'
);