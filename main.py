from flask import Flask
from controllers import UserController

app = Flask(__name__)


@app.route('/signup', methods=['POST'])
def signup():
    return UserController.cadastrar()


if __name__ == '__main__':
    app.run(debug=True)
