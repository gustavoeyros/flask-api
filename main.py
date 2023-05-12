from flask import Flask, jsonify
from controllers import UserController
from flask_marshmallow import Marshmallow
from routes.routes import routes

app = Flask(__name__)
ma = Marshmallow(app)


app.register_blueprint(routes)


if __name__ == '__main__':
    app.run(debug=True)
