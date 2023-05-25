from flask import Blueprint, jsonify
from controllers import UserController, NeuralNController

routes = Blueprint('routes', __name__)


@routes.route('/signup', methods=['POST'])
def signUp():
    return UserController.signUp()


@routes.route('/signin', methods=['POST'])
def signIn():
    return UserController.signIn()


@routes.route('/saveanimal/<userId>', methods=['POST'])
def saveAnimal(userId):
    return UserController.saveAnimal(userId)


@routes.route('/findanimals/<userId>', methods=['GET'])
def findAnimals(userId):
    return UserController.findAnimals(userId)


@routes.route('/result/<file_id>', methods=['GET'])
def get_image_result(file_id):
    return NeuralNController.process_image(file_id)
