from flask import jsonify
from gridfs import GridFS
from io import BytesIO
from keras.utils import img_to_array
from keras.models import load_model
from PIL import Image
import numpy as np
import cv2
from models.bd import db
from bson import ObjectId


# Load the saved model
model = load_model("my_model.h5")

# Define the classes
class_names = ['healthy', 'unhealthy']


# Create a GridFS object
fs = GridFS(db)


def Complexo(rotacao_image, angulo):
    altura, largura = rotacao_image.shape[0], rotacao_image.shape[1]
    y, x = altura / 2, largura / 2
    rotacao_matriz = cv2.getRotationMatrix2D((x, y), angulo, 1.0)
    coseno = np.abs(rotacao_matriz[0][0])
    seno = np.abs(rotacao_matriz[0][1])
    nova_altura = int((altura * seno) + largura * coseno)
    nova_largura = int((altura * coseno) + largura * seno)
    rotacao_matriz[0][2] += (nova_largura / 2) - x
    rotacao_matriz[1][2] += (nova_altura / 2) - y
    rotacionando_imagem = cv2.warpAffine(
        rotacao_image, rotacao_matriz, (nova_largura, nova_altura))
    return rotacionando_imagem


def process_image(file_id):
    file_id_formatted = ObjectId(file_id)
    # Retrieve the image from MongoDB GridFS
    image_data = fs.get(file_id_formatted)
    image = Image.open(BytesIO(image_data.read()))

    # Apply the "Complexo" function to rotate the image
    rotated_image = Complexo(np.array(image), 360)
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
