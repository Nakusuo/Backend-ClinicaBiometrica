# Medición y análisis (MA)

Cada métrica responde a un objetivo. Se recoge al cerrar cada milestone (los datos salen de GitHub y del CI) y se analiza en la revisión de la fase.

| Objetivo | Métrica | Fuente | Meta |
|---|---|---|---|
| Calidad del código | Cobertura de pruebas del backend | Resumen del job *pruebas* | ≥ 70 % |
| Calidad del producto | Defectos abiertos por severidad | Issues con etiqueta `bug` | 0 críticos o altos al hacer una release |
| Eficacia de la verificación | Defectos hallados por pruebas o revisión antes de `main` / total | Issues `bug` | ≥ 80 % |
| Cumplimiento del plan | Issues cerrados / planeados por milestone | Milestones | ≥ 90 % |
| Trazabilidad | Requisitos *Hecho* con prueba / total *Hecho* | [trazabilidad.md](trazabilidad.md) | 100 % |
| Rendimiento | p95 del login facial | Medición manual (issue B#15) | < 3 s |
| Proceso | PRs unidos con CI verde e issue enlazado / total | PRs | 100 % |

## Registro

### Línea base — 14 oct 2026 (fases 0 a 4 abiertas)

| Métrica | Valor | Comentario |
|---|---|---|
| Cobertura backend | 74 % | Medida en `develop` antes de las pruebas nuevas de la fase 4 |
| Pruebas automáticas | 40 backend + 16 frontend | Más ~12 nuevas en PRs pendientes de unir |
| Defectos registrados | 7 | B#9, B#11, B#19, el estado libre de citas (B#18), F#5, F#6 y el token que el frontend no enviaba (corregido en `fix/fase2-base`) |
| Defectos hallados antes de `main` | 7 / 7 (100 %) | Todos por prueba manual, revisión o al escribir pruebas |
| Requisitos *Hecho* con prueba | 22 / 25 (88 %) | Faltan RF-18, RF-19 y RNF-09; RF-18 y RNF-09 ya tienen prueba en B#18 |
| PRs abiertos en espera de revisión | 17 | Cuello de botella: la revisión. Ver lecciones aprendidas |

## Análisis

- El proceso detectó **todos** los defectos antes de publicar. Tres de ellos (B#18, B#19 y el estado libre) salieron al **escribir las pruebas** de la fase 4, lo que muestra el valor de exigir una prueba por requisito.
- El cuello de botella es la revisión de PRs. Acción: revisar los PRs al final de cada día y no abrir más de 5 sin revisar.
