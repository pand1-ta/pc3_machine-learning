# README — Object Detection with NAO Robot + ResNet18 (Pascal VOC)

Proyecto desarrollado como parte de la práctica de visión artificial con el robot NAO.
Implementa un sistema cliente–servidor capaz de detectar objetos en tiempo real utilizando el dataset Pascal VOC 2012, un modelo ResNet18 entrenado en PyTorch y ejecutado en un servidor externo mediante ONNX Runtime.

## Objetivo del Proyecto
Desarrollar un sistema que permita al robot NAO capturar imágenes, enviarlas por red hacia un servidor de inferencia, donde un modelo ResNet18 entrenado con 20 clases del Pascal VOC realiza la predicción y devuelve la etiqueta al robot, quien la anuncia mediante TTS.

## Arquitectura General
El sistema sigue un enfoque cliente–servidor:

### Robot NAO (Python 2.7 — NAOqi SDK)

**Funcionalidades:**
- Captura imágenes mediante ALVideoDevice
- Convierte los bytes RGB en formato serializable
- Envía las imágenes al servidor mediante sockets TCP
- Recibe la predicción enviada por el servidor
- Anuncia la clase detectada con ALTextToSpeech
- Guarda las imágenes capturadas en formato JPG (para auditoría)

### Servidor de Inferencia (Python 3.x)
- Recibe la imagen desde NAO (estructura pickle serializada)
- Reconstruye la imagen usando Pillow
- Preprocesa la imagen para ResNet18
- Ejecuta inferencia usando ONNX Runtime
- Retorna la clase detectada al NAO

## Modelo de Deep Learning
- **Arquitectura:** ResNet18 (pre-entrenada en ImageNet)
- **Última capa reemplazada para 20 clases del Pascal VOC**
- **Entrenado usando:**
  - PyTorch
  - Aumento de datos
  - Congelamiento de capas base
  - Optimización Adam

**Clases soportadas:**
~~~ 
aeroplane, bicycle, bird, boat, bottle,
bus, car, cat, chair, cow,
diningtable, dog, horse, motorbike, person,
pottedplant, sheep, sofa, train, tvmonitor
~~~

## Tecnologías Utilizadas

### Robot NAO
- Python 2.7
- NAOqi SDK
- ALVideoDevice
- ALTextToSpeech
- TCP sockets
- pickle (protocol=2)

### Servidor
- Python 3.10+
- ONNX Runtime
- Pillow
- NumPy
- Sockets TCP
- ResNet18 exportado a ONNX

### Entrenamiento del Modelo
- PyTorch
- Torchvision
- Pascal VOC 2012
- Matplotlib & Seaborn (visualización)
- ONNX + ONNX-TF

## Estructura del Proyecto
~~~
ObjectDetection-NAO-ResNet18/
│
├── modelo/
│   ├── pc3_machine.ipynb
│   ├── resnet18_voc.onnx
│
├── servidor/
│   └── servidor.py
│
├── nao /
│   └── Nao.py
│
├── README.md
└── requirements.txt
~~~

## Cómo Ejecutar el Servidor (Python 3.x)

1. Instalar dependencias:
~~~bash
pip install onnxruntime pillow numpy
~~~

2. Colocar el archivo del modelo:
~~~
resnet18_voc.onnx
~~~

3. Ejecutar el servidor:
~~~bash
cd servidor/
python servidor_onnx_voc.py
~~~

**El servidor escuchará en:**
~~~
HOST = 0.0.0.0
PORT = 8080
~~~

## Cómo Ejecutar el Cliente en NAO

1. Conectar al robot e instalar dependencias (en NAO):
~~~bash
pip2 install pillow
~~~

2. Editar la IP del robot y del servidor en el script:
~~~python
ROBOT_IP = "xxx.xxx.xxx.xxx"
SERVER_IP = "xxx.xxx.xxx.xxx"
~~~

3. Ejecutar el script Python 2.7:
~~~bash
cd nao_client/
python nao_detect_pascalvoc.py
~~~

## Flujo de Detección

1. NAO solicita al usuario mostrar un objeto.
2. Toma la fotografía → convierte los bytes → la envía al servidor.
3. El servidor reconstruye la imagen y ejecuta inferencia ONNX.
4. Devuelve la etiqueta predicha.
5. NAO anuncia el nombre del objeto.
6. Se repite el proceso para múltiples capturas.

## Video de Demostración:

https://youtu.be/eHMvQ3p2VAQhttps://youtu.be/eHMvQ3p2VAQ
