# ADR-0003: Esquema versionado con Alembic

**Estado:** aceptada · **Fecha:** 2026-10

## Contexto
El esquema se creaba con `create_all` y un `Query.sql` manual que se desincronizaba de los modelos.

## Opciones
1. **Alembic** con migraciones revisadas en cada PR.
2. Seguir con `create_all` y scripts SQL a mano.

## Decisión
Opción 1. Cada cambio de modelo trae su migración; el CI comprueba que las migraciones producen el mismo esquema que los modelos y que el downgrade funciona.

## Consecuencias
- (+) El esquema es un elemento de configuración más (ver [gestion-configuracion.md](../cmmi/gestion-configuracion.md)).
- (−) Hay que revisar las migraciones autogeneradas antes de subirlas.
