from marshmallow import Schema, fields


class UserSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class AnimalSchema(Schema):
    name = fields.String(required=True)
    color = fields.String(required=True)
    image = fields.Field(required=True)
