# Aseguramiento de calidad (PPQA)

Objetivo: comprobar de forma objetiva que el **proceso** (CM, requisitos, pruebas) se sigue y que el **producto** cumple sus estándares.

## Estándares del producto

| Qué | Estándar | Cómo se comprueba |
|---|---|---|
| Estilo Python | `ruff` sin errores | CI (`ruff check .`) |
| Tests del backend | `pytest` en verde | CI, en SQLite y PostgreSQL |
| Migraciones | Coinciden con los modelos | `tests/test_migraciones.py` en CI |
| Tests del frontend | Karma/Jasmine en verde | CI (Chrome headless) |
| Build | `ng build` de producción y la imagen Docker compilan | CI |
| Seguridad | Cada usuario solo accede a lo suyo | `tests/test_seguridad.py` |

## Revisión de cada cambio

Cada PR usa la plantilla con su checklist. Un PR no se une si:
- el CI falla,
- no enlaza un issue (`Closes #N`),
- cambia comportamiento sin un test que lo cubra.

## Auditorías del proceso

Al cerrar cada milestone se revisa una muestra de PRs y se anota el resultado en un issue con etiqueta `ppqa`:

| Pregunta | Evidencia |
|---|---|
| ¿Cada PR enlaza un issue? | Descripción del PR |
| ¿La rama siguió la convención? | Nombre de la rama |
| ¿El CI pasó antes del merge? | Checks del PR |
| ¿Se unió con merge commit? | `git log --graph` |
| ¿Los issues tienen requisito y criterios de aceptación? | Cuerpo del issue |

Las **no conformidades** se registran como issue con etiquetas `ppqa` y `bug` y se siguen hasta cerrarlas.
