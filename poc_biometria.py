import face_recognition
import cv2
import numpy as np
import os

print("=== S1: PRUEBA DE CONCEPTO BIOMÉTRICA INTERGRANTE 4 ===")

ruta_imagen = "app/pruebas_biometria/foto_doctor.jpg"

if not os.path.exists(ruta_imagen):
    print("\n[!] Estructura lista. Para correr la simulación de imágenes de la S1, recuerda guardar una foto en la ruta especificada.")
else:
    img = cv2.imread(ruta_imagen)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb)
    if encodings:
        print(f"-> Embedding generado con éxito de manera local usando face_recognition.")
        print(f"-> Dimensiones del vector (debe ser 128): {len(encodings[0])}")