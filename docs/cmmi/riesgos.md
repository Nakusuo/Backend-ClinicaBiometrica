# Gestión de riesgos (RSKM)

Probabilidad (P) e impacto (I) de 1 a 3; **exposición = P × I**. Los riesgos con exposición de 6 o más tienen plan de mitigación activo. La lista se revisa al cerrar cada milestone.

| ID | Riesgo | P | I | Exp. | Mitigación | Contingencia | Estado |
|---|---|---|---|---|---|---|---|
| R-01 | El reconocimiento facial falla con mala luz o cámaras malas y bloquea el acceso | 3 | 2 | 6 | Login con contraseña como alternativa (RF-05); umbral documentado en ADR-0002 | Registrar de nuevo el rostro desde *Mi rostro* | Mitigado |
| R-02 | Fuga de datos clínicos entre usuarios | 2 | 3 | 6 | Pruebas de permisos en `test_seguridad.py` en cada PR | Hotfix desde `main` | Mitigado |
| R-03 | La videollamada WebRTC no conecta detrás de NAT estricto | 2 | 3 | 6 | Probar en redes distintas antes de la entrega | Servidor TURN; o demo en la misma red | Abierto |
| R-04 | No llegar a la fecha de entrega | 2 | 3 | 6 | Prioridades A/M/B; milestones con seguimiento semanal | Recortar requisitos M | Abierto |
| R-05 | FreePBX no está disponible para la demo | 2 | 2 | 4 | La integración es de solo lectura y opcional | Mostrar con datos de ejemplo | Abierto |
| R-06 | Secretos subidos al repositorio | 1 | 3 | 3 | `.env` ignorado; plantilla `.env.example`; checklist del PR | Rotar la clave y limpiar el historial | Mitigado |
| R-07 | Cambio de esquema rompe datos existentes | 1 | 3 | 3 | Migraciones Alembic probadas en CI (upgrade y downgrade) | `alembic downgrade` y respaldo | Mitigado |
| R-08 | Una dependencia nueva rompe el build | 2 | 1 | 2 | Versiones fijas; CI en cada PR | Volver a la versión anterior del lock | Mitigado |
