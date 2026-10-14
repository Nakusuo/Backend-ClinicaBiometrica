# Lecciones aprendidas (OPF)

Se completan al cerrar cada fase. Cada lección termina en una **acción** que cambia el proceso, y la acción se refleja en el documento correspondiente.

| Fecha | Qué pasó | Lección | Acción |
|---|---|---|---|
| 2026-10-14 | `develop` llevaba 4 meses sin actualizarse y una rama con arreglos importantes (`fix/fase2-base`) no se había unido nunca | Una rama que no se integra se pierde | Gitflow con `develop` vigente; las ramas viejas pasan a `archivo/` ([gestion-configuracion.md](gestion-configuracion.md)) |
| 2026-10-14 | En `main` el frontend nunca enviaba el token: todas las pantallas daban 401 y nadie lo notó | Sin pruebas de integración, "compila" no significa "funciona" | Pruebas del interceptor y prueba de aceptación PA-04 |
| 2026-10-14 | Al escribir las pruebas de RF-11 aparecieron dos huecos de permisos (estado libre, PUT del paciente) | Escribir la prueba desde el requisito encuentra defectos que la revisión no ve | Toda fila *Hecho* de la matriz necesita prueba ([trazabilidad.md](trazabilidad.md)) |
| 2026-10-14 | El panel decía "Citas de Hoy" pero mostraba todas, y las citas demo tenían fecha fija | Los datos de prueba también son código: si envejecen, esconden defectos | Datos demo relativos a la fecha actual, con prueba (B#9) |
| 2026-10-14 | Se acumularon 17 PRs esperando revisión | El trabajo no termina hasta que se une | Revisión diaria y un límite de PRs abiertos ([metricas.md](metricas.md)) |
