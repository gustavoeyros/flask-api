from flask import Blueprint, jsonify
from controllers import UserController, NeuralNController

routes = Blueprint('routes', __name__)


@routes.route('/signup', methods=['POST'])
def signUp():
    return UserController.signUp()


@routes.route('/signin', methods=['POST'])
def signIn():
    return UserController.signIn()


@routes.route('/newanimal/<userId>', methods=['POST'])
def saveAnimal(userId):
    return UserController.saveAnimal(userId)


@routes.route('/findanimals/<userId>', methods=['GET'])
def findAnimals(userId):
    return UserController.findAnimals(userId)


@routes.route('/storeprediagnosis/<userId>/<animalId>', methods=['POST'])
def storeAnimal(userId, animalId):
    return UserController.storePreDiagnosis(userId, animalId)


@routes.route('/result/<file_id>', methods=['GET'])
def get_image_result(file_id):
    predicted_class, confidence = NeuralNController.process_image(file_id)
    results = {
        'predicted_class': predicted_class,
        'confidence': confidence
    }
    return jsonify(results)


@routes.route('/delete/<userId>/<animalId>', methods=['DELETE'])
def deleteAnimal(userId, animalId):
    return UserController.deleteAnimal(userId, animalId)


@routes.route('/updateuser/<userId>', methods=['PUT'])
def updateUser(userId):
    return UserController.updateUser(userId)


@routes.route('/verifyuser/<userId>', methods=['GET'])
def verifyUser(userId):
    return UserController.verifyUser(userId)


@routes.route('/updateanimal/<userId>/<animalId>', methods=['PUT'])
def updateAnimal(userId, animalId):
    return UserController.updateAnimal(userId, animalId)
