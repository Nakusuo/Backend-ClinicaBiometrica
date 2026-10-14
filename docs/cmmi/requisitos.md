# Especificación de requisitos (RD)

Plataforma de telemedicina para una clínica: médicos y pacientes entran con su rostro o con su contraseña, agendan citas, llevan el expediente clínico y se atienden por videollamada.

**Actores:** Paciente, Médico, Central telefónica (FreePBX/Asterisk).

Prioridad: **A** imprescindible para la entrega · **M** deseable · **B** si sobra tiempo.
Estado: **Hecho** (implementado y con prueba) · **Parcial** · **Pendiente**.

Cada requisito se rastrea hasta el código, las pruebas y los issues en [trazabilidad.md](trazabilidad.md). Un cambio en esta lista se hace por PR, con un issue de la plantilla *Requisito o mejora*.

## Requisitos funcionales

### Acceso

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-01 | El paciente se registra con DNI, nombres, correo, teléfono, fecha de nacimiento y contraseña. | A | Hecho |
| RF-02 | El médico se registra con especialidad y cédula; su cuenta queda pendiente hasta que un médico activo la apruebe. | A | Hecho |
| RF-03 | El usuario registra su rostro (al crear la cuenta o después, en *Mi rostro*). | A | Hecho |
| RF-04 | El usuario inicia sesión con su rostro: el sistema compara el vector facial con el registrado. | A | Hecho |
| RF-05 | El usuario inicia sesión con correo y contraseña. | A | Hecho |
| RF-06 | Cada rol entra solo a su panel; la sesión vence y se cierra al expirar el token. | A | Hecho |

### Citas

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-07 | El paciente agenda una cita eligiendo médico, fecha, hora y motivo. | A | Hecho |
| RF-08 | No se agendan citas en el pasado ni en un horario que el médico ya tiene ocupado. | A | Hecho |
| RF-09 | El médico ve sus citas de hoy y, a pedido, todas sus citas. | A | Hecho |
| RF-10 | El paciente ve su próxima cita y su historial de citas. | A | Hecho |
| RF-11 | El médico cambia el estado de una cita (programada, en curso, finalizada, cancelada). | M | Hecho |
| RF-12 | El paciente cancela o reprograma su cita. | M | Hecho |

### Expediente clínico

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-13 | El médico registra la consulta: diagnóstico, receta y exámenes; queda firmada por él. | A | Hecho |
| RF-14 | El médico y el paciente consultan el expediente del paciente; el paciente solo el suyo. | A | Hecho |
| RF-15 | El médico ve su historial reciente de consultas. | M | Hecho |

### Videollamada

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-16 | El paciente solicita la videollamada de su cita y el médico la acepta. | A | Hecho |
| RF-17 | La señalización WebRTC solo conecta a los participantes de la cita. | A | Hecho |
| RF-18 | Al terminar, la llamada queda registrada con su duración. | M | Hecho |

### Integración con telefonía

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-19 | El sistema lee el historial de llamadas (CDR) de FreePBX en solo lectura. | M | Hecho |
| RF-20 | El sistema recibe eventos de Asterisk por webhook autenticado. | M | Hecho |

## Requisitos no funcionales

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RNF-01 | **Seguridad:** toda ruta de la API exige token JWT, salvo login y registro. | A | Hecho |
| RNF-02 | **Privacidad:** cada usuario accede solo a sus datos; la foto del rostro nunca sale del navegador, solo el vector. | A | Hecho |
| RNF-03 | **Integridad clínica:** la API no inventa datos clínicos; lo no registrado se muestra como tal. | A | Hecho |
| RNF-04 | **Mantenibilidad:** el esquema de la base se versiona con migraciones; las dependencias tienen versiones fijas. | A | Hecho |
| RNF-05 | **Calidad:** cada cambio pasa tests, lint y build en CI antes de unirse. | A | Hecho |
| RNF-06 | **Portabilidad:** la API corre con Docker (PostgreSQL) y en local con SQLite. | M | Hecho |
| RNF-07 | **Rendimiento:** el login facial responde en menos de 3 s en una red normal. | M | Parcial: API medida (p95 5 ms); falta la detección en el navegador |
| RNF-08 | **Usabilidad:** las pantallas funcionan en móvil (ancho 360 px). | M | Hecho |
| RNF-09 | **Configuración segura:** en producción la API no arranca con datos de prueba ni con una clave débil. | A | Hecho |
