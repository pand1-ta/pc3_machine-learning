# -*- coding: utf-8 -*-
import socket
import struct
import numpy as np
from PIL import Image
import onnxruntime as ort
from io import BytesIO
import traceback

# ==========================================================
# CONFIGURACION
# ==========================================================
HOST = "0.0.0.0"
PORT = 8080

print("Cargando modelo ONNX...")
session = ort.InferenceSession("resnet18_voc.onnx")
input_name = session.get_inputs()[0].name
print("Modelo cargado correctamente:", input_name)

VOC_CLASSES = [
    "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat",
    "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person",
    "pottedplant", "sheep", "sofa", "train", "tvmonitor"
]

# ==========================================================
# PREPROCESAMIENTO
# ==========================================================
def preprocess_from_bytes(img_bytes, width=640, height=480):
    """Convierte bytes de imagen en tensor normalizado listo para ONNX."""
    try:
        # Abrir imagen desde bytes (compatible JPEG, PNG, etc.)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        print("Error al abrir la imagen:", e)
        # Intentar raw RGB como fallback
        img = Image.frombytes("RGB", (width, height), img_bytes)

    img.save("ultima_captura.jpg")
    print("Imagen reconstruida y guardada como ultima_captura.jpg")

    # Redimensionar a tamaño de entrada del modelo
    img = img.resize((224, 224))
    img_np = np.array(img).astype(np.float32) / 255.0

    # Normalizacion (igual que en Colab)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_np = (img_np - mean) / std

    # Cambiar a formato (1,3,224,224)
    img_np = np.transpose(img_np, (2, 0, 1))[np.newaxis, :, :, :]
    print("Shape del tensor:", img_np.shape, "Tipo:", img_np.dtype)
    return img_np

# ==========================================================
# INFERENCIA
# ==========================================================
def infer(img_bytes):
    """Ejecuta la inferencia ONNX y devuelve la etiqueta predicha."""
    x = preprocess_from_bytes(img_bytes)
    outputs = session.run(None, {input_name: x})
    pred_idx = int(np.argmax(outputs[0]))
    return VOC_CLASSES[pred_idx]

# ==========================================================
# SERVIDOR PRINCIPAL
# ==========================================================
print("Servidor de deteccion ONNX listo en el puerto", PORT)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print("\n========================================")
        print("Conexion desde:", addr)
        with conn:
            try:
                # Recibir longitud del mensaje (4 bytes)
                raw_msglen = conn.recv(4)
                if not raw_msglen:
                    print("No se recibio longitud de mensaje.")
                    continue

                msglen = struct.unpack("!I", raw_msglen)[0]
                print("Longitud declarada:", msglen)

                # Recibir todos los bytes de la imagen
                data = b""
                while len(data) < msglen:
                    packet = conn.recv(min(4096, msglen - len(data)))
                    if not packet:
                        break
                    data += packet

                if len(data) != msglen:
                    print(f"No se recibieron todos los bytes. Esperado: {msglen}, Recibido: {len(data)}")
                    conn.sendall(b"-1")
                    continue

                print("Bytes totales recibidos:", len(data))

                # Ejecutar inferencia
                label = infer(data)
                print("Prediccion:", label)
                conn.sendall(label.encode("utf-8"))

            except Exception as e:
                print("Error procesando:", repr(e))
                traceback.print_exc()
                try:
                    conn.sendall(f"ERROR:{repr(e)}".encode("utf-8"))
                except:
                    pass
