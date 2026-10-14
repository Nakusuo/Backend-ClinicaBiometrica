# Cambios

Formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/).

## [1.0.0] - 2026-10-14

Primera versión publicada bajo el proceso CMMI nivel 3 ([docs/cmmi](docs/cmmi/README.md)).

### Añadido
- Autenticación con JWT y permisos por rol en toda la API; token del WebSocket fuera de la URL.
- Migraciones con Alembic y versiones de dependencias fijas.
- Registro de rostro después de crear la cuenta; consultas recientes del médico.
- Validación de citas: no en el pasado ni en un horario ocupado (#11).
- El paciente cancela y reprograma su cita; solo el médico cambia los demás estados (#14, #19).
- CI con lint, pruebas en SQLite y PostgreSQL, cobertura mínima de 70 % e imagen Docker.
- Documentación del proceso: requisitos, trazabilidad, plan, riesgos, ADRs, verificación y validación, métricas.
- Pruebas de aceptación automatizadas por API (`scripts/aceptacion_api.py`).

### Corregido
- La API ya no inventa datos clínicos.
- Las citas de prueba se crean con la fecha actual (#9).
