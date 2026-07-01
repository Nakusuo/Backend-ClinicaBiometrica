from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.models.paciente import Paciente
from app.models.cita import Cita
from app.models.expediente import Expediente
from app.models.consulta import Consulta
from app.models.receta import Receta
import bcrypt
import json

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def seed_db(db: Session):
    # 0. Crear Administrador de prueba si no existe
    admin_exists = db.query(Doctor).filter(Doctor.rol == "admin").first()
    if not admin_exists:
        admin = Doctor(
            nombres="Administrador",
            apellidos="Clínica",
            correo="admin@email.com",
            especialidad="Administrador",
            cedula="ADM001",
            telefono="+51 999 000 000",
            password_hash=hash_password("admin123"),
            embedding_facial=None,
            rol="admin",
            activo=True
        )
        db.add(admin)
        db.flush()
        print("Admin user seeded successfully!")

    # Verificar si ya existen doctores comunes
    if db.query(Doctor).filter(Doctor.rol == "doctor").count() > 0:
        db.commit()
        return

    # 1. Crear Doctor de prueba
    doctor = Doctor(
        nombres="Carlos",
        apellidos="Mendoza",
        correo="doctor@email.com",
        especialidad="Medicina General",
        cedula="CMP12345",
        telefono="+51 999 111 222",
        password_hash=hash_password("password123"),
        # Embedding de 128 floats (relleno con 0.1 como en el bypass del front)
        embedding_facial=json.dumps([0.1] * 128),
        rol="doctor",
        activo=True
    )
    db.add(doctor)
    db.flush()

    # 2. Crear Paciente de prueba
    paciente = Paciente(
        dni="76543210",
        nombres="María",
        apellidos="Delgado",
        telefono="+51 987 654 321",
        correo="maria@email.com",
        fecha_nacimiento="1995-10-20",
        direccion="Av. Larco 456, Miraflores",
        genero="Femenino",
        password_hash=hash_password("password123"),
        embedding_facial=json.dumps([0.1] * 128)
    )
    db.add(paciente)
    db.flush()

    # 3. Crear Citas de prueba
    cita1 = Cita(
        paciente_id=paciente.id,
        doctor_id=doctor.id,
        fecha="2026-06-23",
        hora="10:00 AM",
        estado="programada",
        motivo="Revisión General Anual"
    )
    cita2 = Cita(
        paciente_id=paciente.id,
        doctor_id=doctor.id,
        fecha="2026-06-23",
        hora="11:15 AM",
        estado="en_curso",
        motivo="Consulta de Seguimiento Post-Operativo"
    )
    db.add(cita1)
    db.add(cita2)
    db.flush()

    # 4. Crear expediente de prueba inicial
    expediente = Expediente(
        paciente_id=paciente.id,
        alergias_conocidas="Polen, Penicilina",
        padecimientos_cronicos="Ninguno",
        grupo_sanguineo="O",
        factor_rh="+",
        historial_resumido="Paciente sin antecedentes de enfermedades de alto riesgo.",
        antecedentes_familiares="Padre hipertenso.",
        antecedentes_quirurgicos="Apendicectomía a los 12 años.",
        habitos_salud="No fuma, ejercicio regular."
    )
    db.add(expediente)
    db.flush()

    # 5. Crear consulta histórica asociada al expediente
    consulta = Consulta(
        expediente_id=expediente.id,
        doctor_id=doctor.id,
        cita_id=None,
        motivo_consulta="Fiebre y dolor de garganta",
        sintomas="Dolor de garganta agudo, fatiga",
        diagnostico_principal="Gripe común en remisión",
        notas_doctor="Paciente muestra mejoría clínica notable.",
        tipo_consulta="General",
        estado="completada"
    )
    db.add(consulta)
    db.flush()

    # 6. Crear receta médica histórica asociada
    receta = Receta(
        consulta_id=consulta.id,
        paciente_id=paciente.id,
        doctor_id=doctor.id,
        nombre_medicamento="Paracetamol 500mg cada 8 horas por 3 días",
        concentracion="500mg",
        presentacion="tabletas",
        dosis="1 tableta cada 8 horas",
        frecuencia="cada 8 horas",
        duracion_tratamiento="3 días",
        indicaciones_especiales="Tomar después de los alimentos."
    )
    db.add(receta)

    db.commit()
    print("Database successfully seeded with new schema!")
