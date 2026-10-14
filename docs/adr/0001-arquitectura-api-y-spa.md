# ADR-0001: API FastAPI separada de una SPA en Angular

**Estado:** aceptada · **Fecha:** 2026-06 (registrada en 2026-10)

## Contexto
El curso pedía *integrar sistemas*: base clínica, central telefónica y portal web. El navegador no debe hablar directo con ninguna base ni con la central.

## Opciones
1. **API REST (FastAPI) + SPA (Angular)** en repos separados.
2. Monolito con plantillas del lado del servidor (Django).
3. Backend en Spring Boot + Angular.

## Decisión
Opción 1. FastAPI genera Swagger solo (útil para integrar y evaluar), es liviano para WebSocket (señalización WebRTC) y Python facilita la parte biométrica. Angular ya era la tecnología del equipo.

## Consecuencias
- (+) Cada parte se despliega y prueba por separado; el contrato es la API.
- (−) Dos repos que hay que versionar juntos: la documentación del proceso se centraliza en el backend.
