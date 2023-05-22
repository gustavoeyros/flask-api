from flask import request, jsonify
from models.bd import db
from schemas.schemas import UserSchema, LoginSchema, AnimalSchema
from bson import ObjectId


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
    user['_id'] = str(user['_id'])
    if user:
        # Usuário encontrado, pode prosseguir com o login
        return jsonify({'message': 'Login bem-sucedido!', 'user': user})
    else:
        # Usuário não encontrado
        return jsonify({'error': 'Credenciais inválidas'}), 401


def saveAnimal(userId):
    animalSchema = AnimalSchema()
    errors = animalSchema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    data = request.get_json()
    user_id = ObjectId(userId)
    user_collection = db['users']
    user = user_collection.find_one({'_id': user_id})

    if user:
        animal_collection = db['animals']
        animal_collection.insert_one(
            {'user_id': user_id, 'animal': data})

        return jsonify({'message': 'Animal registrado com sucesso!'})
    else:
        # User not found
        return jsonify({'error': 'Usuário não encontrado!'}), 404


def findAnimals(userId):
    user_id = ObjectId(userId)
    user_collection = db['users']
    user = user_collection.find_one({'_id': user_id})

    if user:
        animal_collection = db['animals']
        animals = animal_collection.find({'user_id': user_id})

        animal_list = []
        for animal in animals:
            animal_info = animal['animal']
            animal_list.append(animal_info)

        return jsonify({'animals': animal_list})
    else:
        return jsonify({'error': 'Usuário não encontrado!'}), 404
