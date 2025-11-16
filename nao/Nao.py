# -*- coding: utf-8 -*-
import socket
import pickle
from naoqi import ALProxy
import time
import struct
import os
import datetime
from PIL import Image

# CONFIGURACION
ROBOT_IP = "10.36.30.36"
PORT = 9559
SERVER_IP = "192.168.56.1"
SERVER_PORT = 8080

RESOLUTION = 2  # 640x480
COLOR_SPACE = 11  # RGB
FPS = 6

CAPTURE_DIR = "capturas_rps"
if not os.path.exists(CAPTURE_DIR):
    os.makedirs(CAPTURE_DIR)

# FUNCIONES

def save_image(img_bytes, width, height, player_id):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(CAPTURE_DIR, "jugador_%d_%s.jpg" % (player_id, timestamp))
        image = Image.frombytes("RGB", (width, height), img_bytes)
        image.save(filename, "JPEG")
        print("Imagen JPG guardada:", filename)
        print("Dimensiones: {}x{}".format(width, height))
    except Exception as e:
        print("ERROR guardando imagen:", e)

def capture_image(video_proxy):
    try:
        nameId = video_proxy.subscribeCamera("rps_cam", 0, RESOLUTION, COLOR_SPACE, FPS)
        frame = video_proxy.getImageRemote(nameId)
        video_proxy.unsubscribe(nameId)
        width, height = frame[0], frame[1]
        array = frame[6]  # bytes RGB
        return array, width, height
    except Exception as e:
        print("ERROR capturando imagen:", e)
        return None, None, None

def send_to_server(img_bytes, width, height):
    try:
        data = pickle.dumps((img_bytes, width, height), protocol=2)
        data_len = struct.pack("!I", len(data))

        sock = socket.socket()
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(data_len)
        sock.sendall(data)
        sock.shutdown(socket.SHUT_WR)

        result = sock.recv(1024)
        sock.close()

        # Asegurarse de que es str en Python 2.7
        if isinstance(result, unicode):
            return result.encode('utf-8')
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        print("ERROR enviando imagen al servidor:", e)
        return "_"

def safe_say(tts, text):
    try:
        # Convertir unicode a str en UTF-8 si es necesario
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        tts.say(text)
    except Exception as e:
        print("Error al decir texto:", e)

# PROGRAMA PRINCIPAL
def main():
    print("Conectando al NAO/simulador...")
    video = ALProxy("ALVideoDevice", ROBOT_IP, PORT)
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)

    safe_say(tts, "Iniciando reconocimiento de objetos.")
    time.sleep(1)

    for i in range(5):
        safe_say(tts, "Por favor, muestra el objeto numero %d." % (i + 1))
        time.sleep(3)

        img_bytes, width, height = capture_image(video)
        if img_bytes is None:
            safe_say(tts, "No pude capturar la imagen.")
            continue

        save_image(img_bytes, width, height, i)
        safe_say(tts, "Analizando la imagen, un momento por favor.")

        pred = send_to_server(img_bytes, width, height)
        if not pred or pred == "_":
            safe_say(tts, "No pude detectar ningun objeto.")
        else:
            # Convertir pred a str seguro
            if isinstance(pred, unicode):
                pred = pred.encode('utf-8')
            safe_say(tts, "Detecte el siguiente objeto: " + pred)
            print("Resultado deteccion #%d: %s" % (i + 1, pred))

        time.sleep(2)

    safe_say(tts, "Proceso de deteccion terminado. Gracias.")
    print("=== Proceso finalizado ===")

if __name__ == "__main__":
    main()
