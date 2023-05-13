from flask import Blueprint
from controllers import UserController

routes = Blueprint('routes', __name__)


@routes.route('/signup', methods=['POST'])
def signup():
    return UserController.signUp()


@routes.route('/signin', methods=['POST'])
def signin():
    return UserController.signIn()
