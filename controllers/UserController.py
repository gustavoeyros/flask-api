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


def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verifique se o usuário existe no banco de dados
    collection = db['users']
    user = collection.find_one({'email': email, 'password': password})

    if user:
        # Usuário encontrado, pode prosseguir com o login
        return jsonify({'message': 'Login bem-sucedido!'})
    else:
        # Usuário não encontrado
        return jsonify({'error': 'Credenciais inválidas'}), 401
