from flask import request, jsonify
from models.bd import db
from schemas.schemas import UserSchema


def cadastrar():
    userSchema = UserSchema()
    errors = userSchema.validate(request.json)
    if errors:
        return jsonify(errors), 400
    data = request.get_json()
    collection = db['users']
    collection.insert_one(data)
    return jsonify({'message': 'Usuário cadastrado com sucesso!'})
