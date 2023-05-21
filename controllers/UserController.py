from flask import request, jsonify
from models.bd import db
from schemas.schemas import UserSchema, LoginSchema, AnimalSchema


def signUp():
    userSchema = UserSchema()
    errors = userSchema.validate(request.json)
    if errors:
        return jsonify(errors), 400
    data = request.get_json()
    collection = db['users']
    collection.insert_one(data)
    return jsonify({'message': 'Usuário cadastrado com sucesso!'})


def signIn():
    loginSchema = LoginSchema()
    errors = loginSchema.validate(request.json)
    if errors:
        return jsonify(errors), 400
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


def saveAnimal():
    animalSchema = AnimalSchema()
    errors = animalSchema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    data = request.get_json()
    user_id = data.get('user_id')
    animal_data = data.get('animal')

    user_collection = db['users']
    user = user_collection.find_one({'_id': user_id})

    if user:
        animal_collection = db['animals']
        animal_collection.insert_one(
            {'user_id': user_id, 'animal': animal_data})

        return jsonify({'message': 'Animal registrado com sucesso!'})
    else:
        # User not found
        return jsonify({'error': 'Usuário não encontrado!'}), 404
