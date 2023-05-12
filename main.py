from flask import Flask, jsonify
from controllers import UserController
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)


@app.route('/signup', methods=['POST'])
def signup():
    return UserController.cadastrar()


if __name__ == '__main__':
    app.run(debug=True)
