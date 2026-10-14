# Plan del proyecto (PP / PMC)

> **Supuesto:** entrega final el **25 de noviembre de 2026**. Si la fecha del curso es otra, se mueven los milestones y esta tabla en el mismo PR.

## Alcance

Lo que se entrega son los requisitos de prioridad **A** de [requisitos.md](requisitos.md) funcionando de punta a punta, más la evidencia CMMI nivel 3 de esta carpeta. Lo **M** entra si el cronograma lo permite y lo **B** queda fuera.

## Cronograma

Cada fase es un **milestone de GitHub** en los dos repos y cada tarea es un issue asignado a su milestone.

| Fase | Milestone | Entregables | Fecha límite |
|---|---|---|---|
| 0 | Fase 0 - Funcional | App de punta a punta: agendar, panel, login con contraseña | 17 oct |
| 1 | Fase 1 - Proceso base | CI en develop, plantillas, CM y PPQA | 21 oct |
| 2 | Fase 2 - Requisitos | Requisitos y matriz de trazabilidad | 24 oct |
| 3 | Fase 3 - Plan y riesgos | Este plan, riesgos, ADRs y arquitectura | 31 oct |
| 4 | Fase 4 - Verificación y validación | Pruebas faltantes, cobertura en CI, RF-12 y pruebas de aceptación | 14 nov |
| 5 | Fase 5 - Medición y cierre | Métricas, release v1.0.0 y lecciones aprendidas | 25 nov |

## Estimación

Estimación por tamaño de issue: **S** (≤ 2 h), **M** (≤ 1 día) y **L** (≤ 3 días). Las tareas L se parten antes de empezar. Al cerrar cada milestone se compara lo planeado con lo real en [metricas.md](metricas.md).

## Recursos

| Rol | Responsable |
|---|---|
| Líder del proyecto, desarrollo, QA | Nakusuo |
| Desarrollo (histórico del backend) | Daniela Ojeda |
| Infraestructura | GitHub (repos, Actions, issues), Docker, PostgreSQL |

## Seguimiento (PMC)

- **Semanal:** revisar el tablero de cada milestone (issues abiertos/cerrados) y el estado del CI.
- **Al cerrar un milestone:** auditoría PPQA ([aseguramiento-calidad.md](aseguramiento-calidad.md)), actualizar métricas y revisar los riesgos.
- **Desvío:** si un milestone se atrasa más de 3 días, se abre un issue `pmc` con la causa y la acción (recortar alcance M, mover fecha o reasignar).
