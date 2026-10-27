from config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$')


class Usuario:

    def __init__(self, data):
        self.id = data.get('id')
        self.nombre = data.get('nombre')
        self.apellido = data.get('apellido')
        self.email = data.get('email')
        self.password = data.get('password')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')

    # Guardar usuario
    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO usuarios
            (nombre, apellido, email, password, created_at, updated_at)
            VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s, NOW(), NOW());
        """
        return connectToMySQL('voluntame').query_db(query, data)

    # Obtener todos los usuarios
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM usuarios;"
        resultados = connectToMySQL('voluntame').query_db(query)

        usuarios = []
        for usuario in resultados:
            usuarios.append(cls(usuario))

        return usuarios

    # Obtener usuario por ID
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM usuarios WHERE id = %(id)s;"
        resultado = connectToMySQL('voluntame').query_db(query, data)

        if resultado:
            return cls(resultado[0])

        return None

    # Obtener usuario por email
    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connectToMySQL('voluntame').query_db(query, data)

        if resultado:
            return cls(resultado[0])

        return None

    # Validar registro
    @staticmethod
    def validar_registro(data):
        es_valido = True

        if len(data['nombre'].strip()) < 2:
            flash("El nombre debe tener al menos 2 caracteres", "error")
            es_valido = False

        if len(data['apellido'].strip()) < 2:
            flash("El apellido debe tener al menos 2 caracteres", "error")
            es_valido = False

        if not EMAIL_REGEX.match(data['email']):
            flash("Correo electrónico inválido", "error")
            es_valido = False

        if len(data['password']) < 8:
            flash("La contraseña debe tener al menos 8 caracteres", "error")
            es_valido = False

        if data['password'] != data['confirmar_password']:
            flash("Las contraseñas no coinciden", "error")
            es_valido = False

        usuario = Usuario.get_by_email({'email': data['email']})

        if usuario:
            flash("El correo electrónico ya está registrado", "error")
            es_valido = False

        return es_valido