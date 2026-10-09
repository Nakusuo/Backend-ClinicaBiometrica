FROM python:3.10-slim

# Evitar que Python escriba archivos .pyc y habilitar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# La API no usa OpenCV ni DeepFace (el embedding facial se calcula en el navegador),
# así que no hacen falta librerías gráficas del sistema.

WORKDIR /app

# Copiar requirements e instalar dependencias de Python
COPY app/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la API
COPY app /app/app

# No correr como root dentro del contenedor
RUN useradd --create-home --uid 1000 api && chown -R api /app
USER api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
