# Gestión de configuración (CM)

## Elementos de configuración

| Elemento | Dónde vive | Cómo se versiona |
|---|---|---|
| Código del backend (FastAPI) | repo Backend, `app/` | Git |
| Esquema de la base de datos | repo Backend, `migrations/` (Alembic) | Una migración por cambio de modelo |
| Dependencias | `app/requirements.txt`, `package-lock.json` | Versiones fijas |
| Código del frontend (Angular) | repo Frontend, `src/` | Git |
| Configuración por entorno | `.env` (no se versiona), `.env.example`, `src/environments/` | Solo la plantilla va a Git |
| Documentación del proceso | repo Backend, `docs/` | Git, cambia por PR como el código |

## Ramas (gitflow)

| Rama | Para qué | Quién escribe |
|---|---|---|
| `main` | Versión publicada. Cada versión lleva tag `vX.Y.Z` | Solo merges desde `release/*` o `hotfix/*` |
| `develop` | Integración de lo terminado | Solo PRs aprobados |
| `feature/<issue>-<tema>` | Un requisito o mejora | Desarrollador; sale de `develop` |
| `fix/<issue>-<tema>` | Un defecto | Desarrollador; sale de `develop` |
| `release/X.Y.Z` | Preparar versión: pruebas de aceptación y notas | Sale de `develop`, se une a `main` y vuelve a `develop` |
| `hotfix/X.Y.Z` | Defecto urgente en producción | Sale de `main`, se une a `main` y a `develop` |
| `archivo/*` | Ramas antiguas conservadas como historia | Solo lectura |

Todas las uniones usan `merge --no-ff` (botón *Create a merge commit*) para que el historial muestre cada cambio como una unidad.

## Control de cambios

1. Todo cambio nace en un **issue** (plantilla *Defecto* o *Requisito o mejora*) con el ID del requisito.
2. Se trabaja en una rama `feature/` o `fix/` con el número del issue.
3. Se abre un **PR hacia `develop`** con la plantilla y su checklist.
4. El **CI** (GitHub Actions) debe pasar: tests, lint y build.
5. Revisión y aprobación; luego merge.
6. Al publicar, `release/X.Y.Z` → `main` con tag.

`main` y `develop` están protegidas: no aceptan push directo y exigen el CI en verde.

## Versiones

[Versionado semántico](https://semver.org/lang/es/): `MAYOR.MENOR.PARCHE`. Cada tag tiene sus notas en *GitHub Releases* con los issues que cierra.

## Auditoría de configuración

Antes de cada release se comprueba (y se anota en el PR de la release):
- [ ] `main` coincide con el tag publicado.
- [ ] Todos los issues del milestone están cerrados o movidos.
- [ ] Las migraciones aplican desde cero (`test_migraciones.py`).
- [ ] No hay secretos en el repo (`.env` ignorado).
