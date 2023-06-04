from flask import Flask, request, jsonify
from gridfs import GridFS
from io import BytesIO
from keras.utils import img_to_array
from keras.models import load_model
from PIL import Image
import numpy as np
import cv2
from models.bd import db
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the saved model
model = load_model("my_model.h5")

# Define the classes
class_names = ['healthy', 'unhealthy']


# Create a GridFS object
fs = GridFS(db)


def rotacao(rotacao_image, angulo):
  altura, largura = rotacao_image.shape[0], rotacao_image.shape[1]
  y, x = altura /2, largura/2
  rotacao_matriz = cv2.getRotationMatrix2D((x, y), angulo, 1.0)
  rotacionando_imagem = cv2.warpAffine(rotacao_image, rotacao_matriz, (largura, altura))
  return rotacionando_imagem


def process_image(file_id):
    file_id_formatted = ObjectId(file_id)

    image_data = fs.get(file_id_formatted)
    image = Image.open(BytesIO(image_data.read()))

    rotated_image = rotacao(np.array(image), 180)
    rotated_image = Image.fromarray(rotated_image)

    # Resize the rotated image
    resized_image = rotated_image.resize((224, 224))

    # Convert the image to an array and normalize
    image_array = img_to_array(resized_image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    # Make a prediction
    prediction = model.predict(image_array)
    predicted_class_index = np.argmax(prediction)
    predicted_class = class_names[predicted_class_index]
    confidence = prediction[0][predicted_class_index] * 100

    # Return the results
    results = {
        'predicted_class': predicted_class,
        'confidence': confidence
    }
    return predicted_class, confidence
