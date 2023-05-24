from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from routes.routes import routes
from flask_cors import CORS

app = Flask(__name__)
ma = Marshmallow(app)
CORS(app)


app.register_blueprint(routes)


if __name__ == '__main__':
    app.run(debug=True, port=5501)
