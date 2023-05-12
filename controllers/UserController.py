from flask import request, jsonify
from models.bd import db


def cadastrar():
    data = request.get_json()
    collection = db['users']
    collection.insert_one(data)
    return jsonify({'message': 'Usuário cadastrado com sucesso!'})
