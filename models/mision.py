
from config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime


class Mision:

    def __init__(self, data):
        self.id = data.get('id')
        self.nombre = data.get('nombre')
        self.fecha = data.get('fecha')
        self.voluntarios = data.get('voluntarios')
        self.descripcion = data.get('descripcion')
        self.usuario_id = data.get('usuario_id')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')

    # Guardar misión
    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO misiones
            (nombre, fecha, voluntarios, descripcion, usuario_id, created_at, updated_at)
            VALUES (%(nombre)s, %(fecha)s, %(voluntarios)s,
                    %(descripcion)s, %(usuario_id)s, NOW(), NOW());
        """
        return connectToMySQL('voluntame').query_db(query, data)

    # Obtener todas las misiones
    @classmethod
    def get_all(cls):
        query = """
            SELECT * FROM misiones
            ORDER BY fecha ASC;
        """
        resultados = connectToMySQL('voluntame').query_db(query)

        misiones = []
        for mision in resultados or []:
            misiones.append(cls(mision))

        return misiones

    # Obtener misión por ID
    @classmethod
    def get_by_id(cls, data):
        query = """
            SELECT * FROM misiones
            WHERE id = %(id)s;
        """
        resultado = connectToMySQL('voluntame').query_db(query, data)

        if resultado:
            return cls(resultado[0])

        return None

    # Actualizar misión
    @classmethod
    def update(cls, data):
        query = """
            UPDATE misiones
            SET nombre = %(nombre)s,
                fecha = %(fecha)s,
                voluntarios = %(voluntarios)s,
                descripcion = %(descripcion)s,
                updated_at = NOW()
            WHERE id = %(id)s AND usuario_id = %(usuario_id)s;
        """
        return connectToMySQL('voluntame').query_db(query, data)

    # Eliminar misión
    @classmethod
    def delete(cls, data):
        query = """
            DELETE FROM misiones
            WHERE id = %(id)s AND usuario_id = %(usuario_id)s;
        """
        return connectToMySQL('voluntame').query_db(query, data)

    # Obtener voluntarios inscritos
    @classmethod
    def get_voluntarios(cls, data):
        query = """
            SELECT usuarios.id, usuarios.nombre, usuarios.apellido
            FROM usuarios
            JOIN usuarios_has_misiones
                ON usuarios.id = usuarios_has_misiones.usuario_id
            WHERE usuarios_has_misiones.mision_id = %(mision_id)s;
        """
        return connectToMySQL('voluntame').query_db(query, data) or []

    # Comprobar si el usuario está inscrito
    @classmethod
    def esta_inscrito(cls, data):
        query = """
            SELECT * FROM usuarios_has_misiones
            WHERE usuario_id = %(usuario_id)s
            AND mision_id = %(mision_id)s;
        """
        resultado = connectToMySQL('voluntame').query_db(query, data)
        return bool(resultado)

    # Inscribir voluntario
    @classmethod
    def inscribir(cls, data):
        query = """
            INSERT INTO usuarios_has_misiones
            (usuario_id, mision_id)
            VALUES (%(usuario_id)s, %(mision_id)s);
        """
        return connectToMySQL('voluntame').query_db(query, data)

    # Retirar voluntario
    @classmethod
    def retirar(cls, data):
        query = """
            DELETE FROM usuarios_has_misiones
            WHERE usuario_id = %(usuario_id)s
            AND mision_id = %(mision_id)s;
        """
        return connectToMySQL('voluntame').query_db(query, data)

    # Validar misión
    @staticmethod
    def validar_mision(data):
        es_valido = True

        if not data['nombre'].strip():
            flash("El nombre no puede estar vacío", "error")
            es_valido = False

        if not data['descripcion'].strip():
            flash("La descripción no puede estar vacía", "error")
            es_valido = False

        try:
            fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()

            if fecha < datetime.now().date():
                flash("No puedes ingresar una fecha pasada", "error")
                es_valido = False

        except ValueError:
            flash("La fecha no es válida", "error")
            es_valido = False

        try:
            if int(data['voluntarios']) < 1:
                flash("Debe haber al menos un voluntario", "error")
                es_valido = False

        except ValueError:
            flash("Ingresa una cantidad válida de voluntarios", "error")
            es_valido = False

        return es_valido
