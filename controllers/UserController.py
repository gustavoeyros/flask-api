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
from datetime import datetime
from uuid import uuid4
import base64

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
    result = collection.insert_one(data)
    inserted_id = result.inserted_id
    return jsonify({'message': 'Usuário cadastrado com sucesso!', 'user_id': str(inserted_id)})


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


def verifyUser(userId):
    user_id = ObjectId(userId)
    user_collection = db['users']
    user = user_collection.find_one({'_id': user_id})

    if user:
        return jsonify({'message': 'Usuário encontrado!'}), 200
    else:
        return jsonify({'error': 'Usuário não encontrado!'}), 404


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

            animal = {
                'animalID': uuid4().hex,
                'name': name,
                'color': color,
                'image_placeholder_id': str(image_id),
            }

            animal_collection = db['animals']
            animal_collection.update_one(
                {'user_id': user_id},
                {'$push': {'animals': animal}},
                upsert=True
            )

            return jsonify({'message': 'Animal registrado com sucesso!', 'animalInfo': animal})
        else:
            return jsonify({'error': 'Usuário não encontrado!'}), 404

    return asyncio.run(saveAnimalAsync())


def storePreDiagnosis(userId, animalId):
    async def storePreDiagnosisAsync():
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

            loop = asyncio.get_event_loop()
            health, confidence = await loop.run_in_executor(None, NeuralNController.process_image, image_id)

            formated_date = datetime.now().strftime('%d/%m/%Y')
            formated_time = datetime.now().strftime('%H:%M:%S')

            animal_collection = db['animals']
            animal = animal_collection.find_one(
                {'user_id': user_id, 'animals.animalID': animalId},
                projection={'animals.$': 1}
            )

            if animal:
                animal_data = animal['animals'][0]
                animal_name = animal_data.get('name')
                animal_color = animal_data.get('color')

                prediagnosis = {
                    'health': health,
                    'accuracy': confidence,
                    'date': formated_date,
                    'time': formated_time,
                    'image_id': str(image_id),
                }

                animal_collection.update_one(
                    {
                        'user_id': user_id,
                        'animals.animalID': animalId
                    },
                    {
                        '$push': {
                            'animals.$.prediagnosis': prediagnosis
                        }
                    }
                )

                animalFormated = {
                    'name': animal_name,
                    'color': animal_color,
                    'prediagnosis': prediagnosis
                }

                return jsonify({'message': 'Pré-diagnóstico realizado com sucesso!', 'animalInfo': animalFormated})
            else:
                return jsonify({'error': 'Animal não encontrado!'}), 404

        else:
            return jsonify({'error': 'Usuário não encontrado!'}), 404

    return asyncio.run(storePreDiagnosisAsync())


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
            for animal_data in animal_info:
                image_id = animal_data.get('image_placeholder_id')
                image = fs.get(ObjectId(image_id))

                # Converte a imagem para Base64
                image_base64 = base64.b64encode(image.read()).decode('utf-8')
                animal_data['image'] = image_base64

            animal_list.append(animal_info)

        return jsonify({'animals': animal_list})
    else:
        return jsonify({'error': 'Usuário não encontrado!'}), 404


def deleteAnimal(userId, animalId):
    user_id = ObjectId(userId)
    animal_collection = db['animals']

    result = animal_collection.update_one(
        {'user_id': user_id},
        {'$pull': {'animals': {'animalID': animalId}}}
    )

    if result.modified_count > 0:
        return jsonify({'message': 'Animal removido com sucesso!'})
    else:
        return jsonify({'error': 'Animal não encontrado!'}), 404


def updateUser(userId):
    user_id = ObjectId(userId)
    user_collection = db['users']
    user = user_collection.find_one({'_id': user_id})

    if user:
        user_schema = UserSchema()
        errors = user_schema.validate(request.json, partial=True)
        if errors:
            return jsonify(errors), 400

        updated_data = request.get_json()
        updated_data.pop('password', None)

        result = user_collection.update_one(
            {'_id': user_id},
            {'$set': updated_data}
        )

        if result.modified_count > 0:
            return jsonify({'message': 'Dados do usuário atualizados com sucesso!'})
        else:
            return jsonify({'error': 'Falha ao atualizar os dados do usuário'}), 500
    else:
        return jsonify({'error': 'Usuário não encontrado!'}), 404


def updateAnimal(userId, animalId):
    user_id = ObjectId(userId)
    animal_collection = db['animals']

    animal_schema = AnimalSchema()
    errors = animal_schema.validate(request.form, partial=True)
    if errors:
        return jsonify(errors), 400

    name = request.form.get('name')
    color = request.form.get('color')
    image = request.files.get('image')

    user_animal = animal_collection.find_one({
        'user_id': user_id,
        'animals.animalID': animalId
    })

    if user_animal:
        animal_index = next(
            (index for index, animal in enumerate(
                user_animal['animals']) if animal['animalID'] == animalId), None
        )

        if animal_index is not None:
            if image:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    image.save(temp_file.name)

                with open(temp_file.name, 'rb') as file:
                    image_id = fs.put(file, filename=image.filename)

                os.remove(temp_file.name)

                animal_collection.update_one(
                    {
                        'user_id': user_id,
                        'animals.animalID': animalId
                    },
                    {
                        '$set': {
                            f'animals.{animal_index}.name': name,
                            f'animals.{animal_index}.color': color,
                            f'animals.{animal_index}.image_placeholder_id': str(image_id),
                        }
                    }
                )
            else:
                animal_collection.update_one(
                    {
                        'user_id': user_id,
                        'animals.animalID': animalId
                    },
                    {
                        '$set': {
                            f'animals.{animal_index}.name': name,
                            f'animals.{animal_index}.color': color,
                        }
                    }
                )

            return jsonify({'message': 'Animal atualizado com sucesso!'})
        else:
            return jsonify({'error': 'Animal não encontrado!'}), 404
    else:
        return jsonify({'error': 'Usuário não encontrado ou animal não encontrado!'}), 404
