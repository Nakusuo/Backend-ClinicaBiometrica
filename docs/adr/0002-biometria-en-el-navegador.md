# ADR-0002: El rostro se procesa en el navegador; el servidor solo compara vectores

**Estado:** aceptada · **Fecha:** 2026-10

## Contexto
El login facial necesita convertir la cara en un descriptor y compararlo con el registrado. La foto es un dato sensible (RNF-02).

## Opciones
1. **face-api.js en el navegador** → envía un vector de 128 valores; el servidor compara con distancia euclidiana.
2. Enviar la foto al servidor y procesarla con DeepFace.
3. Servicio externo de reconocimiento (AWS Rekognition, Azure Face).

## Decisión
Opción 1. La foto nunca sale del dispositivo, el servidor no necesita GPU ni TensorFlow (la imagen Docker es mucho más chica) y no hay costo externo. **Umbral: 0.5** (face-api.js sugiere 0.6; más estricto para reducir falsos positivos). DeepFace queda solo en `poc_biometria.py` como prueba de concepto.

## Consecuencias
- (+) Privacidad y despliegue simple.
- (−) Un cliente modificado podría enviar un vector robado: se mitiga con contraseña alternativa, rol en el token y pruebas (`test_login_facial_*`). No es apto como único factor en un sistema real.
- (−) Depende de la cámara y la luz (riesgo R-01).
