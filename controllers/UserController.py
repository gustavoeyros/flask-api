from flask import request, jsonify
from models.bd import db
from schemas.schemas import UserSchema, LoginSchema, AnimalSchema
from bson import ObjectId
import bcrypt
from gridfs import GridFS
import tempfile
import os
from controllers import NeuralNController
import asyncio

fs = GridFS(db)


def signUp():
    userSchema = UserSchema()
    errors = userSchema.validate(request.json)
    if errors:
        return jsonify(errors), 400
    data = request.get_json()
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    data['password'] = hashed_password
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
    collection = db['users']
    user = collection.find_one({'email': email})
    if user:
        hashed_password = user.get('password').decode(
            'utf-8')  # Converter de BinData para string
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            user['_id'] = str(user['_id'])
            return jsonify({'message': 'Login bem-sucedido!', 'userId': user['_id'], 'name': user['name']})
    # Usuário não encontrado ou credenciais inválidas
    return jsonify({'error': 'Credenciais inválidas'}), 401


def saveAnimal(userId):
    async def saveAnimalAsync():
        animal_schema = AnimalSchema()
        errors = animal_schema.validate(request.form, partial=True)
        if errors:
            return jsonify(errors), 400

        name = request.form.get('name')
        color = request.form.get('color')
        image = request.files['image']

        user_id = ObjectId(userId)
        user_collection = db['users']
        user = user_collection.find_one({'_id': user_id})

        if user:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                image.save(temp_file.name)

            with open(temp_file.name, 'rb') as file:
                image_id = fs.put(file, filename=image.filename)

            os.remove(temp_file.name)

            # Process the image asynchronously to get health
            loop = asyncio.get_event_loop()
            health, confidence = await loop.run_in_executor(None, NeuralNController.process_image, image_id)

            animal = {
                'name': name,
                'color': color,
                'image_id': str(image_id),
                'health': health,
                'accuracy': confidence
            }

            animal_collection = db['animals']
            animal_collection.update_one(
                {'user_id': user_id},
                {'$push': {'animals': animal}},
                upsert=True
            )

            return jsonify({'message': 'Animal registrado com sucesso!'})
        else:
            return jsonify({'error': 'Usuário não encontrado!'}), 404

    return asyncio.run(saveAnimalAsync())


def findAnimals(userId):
    user_id = ObjectId(userId)
    user_collection = db['users']
    user = user_collection.find_one({'_id': user_id})

    if user:
        animal_collection = db['animals']
        animals = animal_collection.find({'user_id': user_id})

        animal_list = []
        for animal in animals:
            animal_info = animal['animals']
            animal_list.append(animal_info)

        return jsonify({'animals': animal_list})
    else:
        return jsonify({'error': 'Usuário não encontrado!'}), 404
