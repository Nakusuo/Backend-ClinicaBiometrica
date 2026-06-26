from deepface import DeepFace
import cv2
import os

print("=== S1: PRUEBA DE CONCEPTO BIOMÉTRICA CON DEEPFACE ===")

ruta_imagen = "app/pruebas_biometria/foto_doctor.jpg"

if not os.path.exists(ruta_imagen):
    print("\n[!] Estructura lista. Para correr la simulación de imágenes de la S1, recuerda guardar una foto en la ruta especificada.")
else:
    try:
        # Generar embedding usando FaceNet (128 dimensiones)
        print(f"Analizando imagen: {ruta_imagen}...")
        resp = DeepFace.represent(img_path=ruta_imagen, model_name="Facenet", enforce_detection=False)
        if resp:
            embedding = resp[0]["embedding"]
            print(f"-> Embedding generado con éxito usando DeepFace (FaceNet)!")
            print(f"-> Dimensiones del vector: {len(embedding)}")
        else:
            print("No se pudieron extraer características faciales.")
    except Exception as e:
        print(f"Error al procesar la imagen con DeepFace: {e}")