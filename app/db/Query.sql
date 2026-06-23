CREATE DATABASE telemedicina;
-- ============================================
-- 1. TABLA: doctores
-- ============================================
CREATE TABLE doctores (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    especialidad VARCHAR(100),
    password_hash TEXT,
    embedding_facial TEXT,
    rol VARCHAR(20) DEFAULT 'doctor',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 2. TABLA: pacientes
-- ============================================
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 3. TABLA: citas
-- ============================================
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctores(id) ON DELETE CASCADE,
    fecha TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'pendiente',
    motivo TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 4. TABLA: expedientes (EXPEDIENTE PRINCIPAL)
-- ============================================
CREATE TABLE expedientes (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,

    -- DATOS BÁSICOS (IDENTIFICACIÓN + ALERGIAS + PADECIMIENTOS CRÓNICOS)
    alergias_conocidas TEXT,           -- Alergias graves
    padecimientos_cronicos TEXT,        -- Enfermedades crónicas
    grupo_sanguineo VARCHAR(5),
    factor_rh VARCHAR(2),

    -- RESUMEN CLÍNICO
    historial_resumido TEXT,            -- Resumen general del paciente
    antecedentes_familiares TEXT,
    antecedentes_quirurgicos TEXT,
    habitos_salud TEXT,                 -- Fuma, alcohol, ejercicio

    -- METADATOS
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_paciente FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- ============================================
-- 5. TABLA: consultas (REGISTRO DE CONSULTAS)
-- ============================================
CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    expediente_id INTEGER REFERENCES expedientes(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctores(id),
    cita_id INTEGER REFERENCES citas(id),

    -- NOTAS DE CONSULTA
    fecha_consulta TIMESTAMP DEFAULT NOW(),
    motivo_consulta TEXT,
    sintomas TEXT,
    signos_vitales JSONB,               -- {presion: "120/80", pulso: 72, temp: 36.5}
    diagnostico_principal TEXT,
    diagnostico_diferencial TEXT,
    notas_doctor TEXT,

    -- ESTADO DE CONSULTA
    tipo_consulta VARCHAR(30),          -- presencial, virtual, urgencia
    estado VARCHAR(20) DEFAULT 'activa', -- activa, completada
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 6. TABLA: recetas (TRATAMIENTOS Y RECETAS)
-- ============================================
CREATE TABLE recetas (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER REFERENCES consultas(id) ON DELETE CASCADE,
    paciente_id INTEGER REFERENCES pacientes(id),
    doctor_id INTEGER REFERENCES doctores(id),

    -- DATOS DE RECETA
    nombre_medicamento VARCHAR(150) NOT NULL,
    concentracion VARCHAR(50),          -- 500mg, 20mg/ml
    presentacion VARCHAR(50),           -- tabletas, jarabe, inyectable
    dosis VARCHAR(100),                 -- 1 tableta cada 8 horas
    frecuencia VARCHAR(100),            -- cada 8 horas, diario, semanal
    duracion_tratamiento VARCHAR(50),   -- 7 días, 1 mes
    indicaciones_especiales TEXT,       -- Tomar con alimentos, etc.

    -- CONTROL
    fecha_receta TIMESTAMP DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 7. TABLA: examenes (LABORATORIO E IMÁGENES)
-- ============================================
CREATE TABLE examenes (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER REFERENCES consultas(id) ON DELETE CASCADE,
    paciente_id INTEGER REFERENCES pacientes(id),
    doctor_solicitante_id INTEGER REFERENCES doctores(id),

    -- DATOS DEL EXAMEN
    tipo_examen VARCHAR(50),            -- laboratorio, imagen, especializado
    nombre_examen VARCHAR(150) NOT NULL, -- Hemograma, Radiografía de tórax
    categoria VARCHAR(50),              -- sangre, orina, rayos X, tomografía, etc.

    -- RESULTADOS
    resultado TEXT,                     -- Descripción textual del resultado
    archivo_url VARCHAR(255),           -- URL del PDF/Imagen (si está digitalizado)
    es_imagen BOOLEAN DEFAULT FALSE,    -- TRUE si es imagen médica

    -- METADATOS
    fecha_solicitud TIMESTAMP DEFAULT NOW(),
    fecha_resultado TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'pendiente', -- pendiente, en_proceso, completado
    notas_doctor TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


-- ============================================
-- 8. TABLA: llamadas (PARA WEBRTC)
-- ============================================
CREATE TABLE llamadas (
    id SERIAL PRIMARY KEY,
    cita_id INTEGER REFERENCES citas(id) ON DELETE CASCADE,
    paciente_id INTEGER REFERENCES pacientes(id),
    doctor_id INTEGER REFERENCES doctores(id),
    room_id VARCHAR(50) UNIQUE,
    estado VARCHAR(20) DEFAULT 'esperando',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duracion INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX idx_doctores_correo ON doctores(correo);
CREATE INDEX idx_pacientes_dni ON pacientes(dni);
CREATE INDEX idx_pacientes_correo ON pacientes(correo);
CREATE INDEX idx_citas_paciente ON citas(paciente_id);
CREATE INDEX idx_citas_doctor ON citas(doctor_id);
CREATE INDEX idx_citas_fecha ON citas(fecha);
CREATE INDEX idx_expedientes_paciente ON expedientes(paciente_id);
CREATE INDEX idx_consultas_expediente ON consultas(expediente_id);
CREATE INDEX idx_consultas_fecha ON consultas(fecha_consulta);
CREATE INDEX idx_recetas_paciente ON recetas(paciente_id);
CREATE INDEX idx_recetas_consulta ON recetas(consulta_id);
CREATE INDEX idx_examenes_paciente ON examenes(paciente_id);
CREATE INDEX idx_examenes_consulta ON examenes(consulta_id);
CREATE INDEX idx_llamadas_room ON llamadas(room_id);

-- ============================================
-- VISTA: HISTORIAL CLÍNICO COMPLETO
-- ============================================
CREATE OR REPLACE VIEW vista_historial_completo AS
SELECT
    p.id as paciente_id,
    p.dni,
    p.nombres || ' ' || p.apellidos as nombre_completo,
    p.fecha_nacimiento,
    p.telefono,
    p.correo,

    -- Datos básicos del expediente
    e.alergias_conocidas,
    e.padecimientos_cronicos,
    e.grupo_sanguineo,
    e.historial_resumido,
    e.antecedentes_familiares,
    e.antecedentes_quirurgicos,

    -- Última consulta
    (
        SELECT jsonb_build_object(
            'fecha', c.fecha_consulta,
            'diagnostico', c.diagnostico_principal,
            'doctor', d.nombres || ' ' || d.apellidos,
            'motivo', c.motivo_consulta
        )
        FROM consultas c
        LEFT JOIN doctores d ON c.doctor_id = d.id
        WHERE c.expediente_id = e.id
        ORDER BY c.fecha_consulta DESC
        LIMIT 1
    ) as ultima_consulta,

    -- Total de consultas
    (SELECT COUNT(*) FROM consultas c WHERE c.expediente_id = e.id) as total_consultas,

    -- Medicamentos activos
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'medicamento', r.nombre_medicamento,
                'dosis', r.dosis,
                'frecuencia', r.frecuencia
            )
               ORDER BY r.fecha_receta DESC
        )
        FROM recetas r
        WHERE r.paciente_id = p.id
        AND r.activo = true
    ) as medicamentos_activos,

    -- Últimos exámenes
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'examen', ex.nombre_examen,
                'tipo', ex.tipo_examen,
                'fecha', ex.fecha_solicitud,
                'resultado', ex.resultado
            )
               ORDER BY ex.fecha_solicitud DESC
        )
        FROM examenes ex
        WHERE ex.paciente_id = p.id
        LIMIT 5
    ) as ultimos_examenes

FROM pacientes p
LEFT JOIN expedientes e ON p.id = e.paciente_id;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;