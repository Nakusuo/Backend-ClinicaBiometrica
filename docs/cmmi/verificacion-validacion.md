# Verificación y validación (VER / VAL)

- **Verificación:** ¿el producto se construyó bien? Pruebas automáticas y revisión de cada PR.
- **Validación:** ¿se construyó el producto correcto? Pruebas de aceptación con usuarios en el entorno real.

## Verificación

| Nivel | Herramienta | Qué cubre | Cuándo |
|---|---|---|---|
| Unitario e integración API | `pytest` + `TestClient` (backend) | Reglas de negocio, permisos, migraciones | Cada push y PR (CI) |
| Unitario frontend | Karma + Jasmine (Chrome headless) | Servicios, guard, interceptor, lógica de pantallas | Cada push y PR (CI) |
| Estático | `ruff`, compilación TypeScript estricta | Errores de código | CI |
| Cobertura | `pytest-cov`, mínimo 70 % | Partes del backend sin probar | CI |
| Revisión entre pares | PR con checklist | Diseño, requisito enlazado, pruebas | Antes de cada merge |

Cada prueba está ligada a su requisito en [trazabilidad.md](trazabilidad.md). Un defecto encontrado se registra como issue `bug` y su arreglo trae una prueba que falla sin él.

## Validación: pruebas de aceptación

Los escenarios que no necesitan cámara ni celular están automatizados en [`scripts/aceptacion_api.py`](../../scripts/aceptacion_api.py) (`python scripts/aceptacion_api.py http://localhost:8000`). El resto se ejecuta a mano. Se ejecutan sobre `develop` antes de cada release, con dos navegadores (médico y paciente) y los datos de prueba (`SEED_DEMO_DATA=true`). El resultado se anota en el PR de la release: ✅ pasa · ❌ falla (con issue).

| ID | Requisitos | Escenario | Resultado esperado |
|---|---|---|---|
| PA-01 | RF-01, RF-03 | Registrar un paciente nuevo con rostro (o *Simular captura*) | La cuenta se crea; el panel muestra el nombre |
| PA-02 | RF-02 | Registrar un médico nuevo e intentar entrar | Queda pendiente; entra después de que otro médico lo active |
| PA-03 | RF-04 | Entrar con el rostro registrado | Entra a su panel en menos de 3 s (RNF-07) |
| PA-04 | RF-05, RF-06 | Entrar con correo y contraseña; abrir la URL del panel del otro rol | Entra al suyo; el otro panel lo devuelve al suyo |
| PA-05 | RF-07, RF-08 | El paciente agenda mañana a las 10:00; un segundo paciente intenta la misma hora con el mismo médico | La primera se crea; la segunda muestra "El médico ya tiene una cita en ese horario" |
| PA-06 | RF-09 | El médico abre su panel; pulsa *Ver todas* | Ve las citas de hoy; luego todas ordenadas por fecha |
| PA-07 | RF-10, RF-12 | El paciente reprograma su cita y luego cancela otra | La fecha cambia; la cancelada se marca y su horario queda libre |
| PA-08 | RF-16, RF-17, RF-18 | El paciente pulsa *Click to Call*; el médico acepta; hablan y cuelgan | Hay audio y video en ambos lados; la llamada queda con su duración |
| PA-09 | RF-13, RF-14 | El médico registra diagnóstico y receta; el paciente abre su expediente | El paciente ve la consulta firmada por su médico |
| PA-10 | RNF-02 | Con la sesión del paciente A, pedir por URL el expediente del paciente B | Acceso denegado |
| PA-11 | RNF-08 | Repetir PA-04 a PA-07 en un celular (360 px) | Todo se puede usar sin desplazamiento horizontal |

## Registro de ejecuciones

| Fecha | Versión | Ejecutó | Resultado | Issues abiertos |
|---|---|---|---|---|
| 2026-10-14 | release/1.0.0 | Script por API | PA-01, 02, 04, 05, 06, 07, 09 y 10: ✅ (8/8) | — |
| 2026-10-14 | v1.0.0 | Iframe de 360 px en cada pantalla | PA-11: ❌ el panel del médico desbordaba 12 px → corregido en F#16; repetido: ✅ en las 8 pantallas | F#16 |
| 2026-10-14 | v1.0.0 | 20 logins faciales por API | PA-03 (parte servidor): ✅ mediana 4 ms, p95 5 ms | B#15 |
| | | | PA-03 con cámara real y PA-08 (videollamada): pendientes, a mano | B#15 |
