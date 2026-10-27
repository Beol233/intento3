from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from models.usuario import Usuario
from __init__ import app

bcrypt = Bcrypt(app)


# Página de inicio
@app.route('/')
def inicio():
    if 'usuario_id' in session:
        return redirect('/dashboard')

    return render_template('index.html')


# Registrar usuario
@app.route('/registrar', methods=['POST'])
def registrar():
    data = {
        'nombre': request.form.get('nombre', '').strip(),
        'apellido': request.form.get('apellido', '').strip(),
        'email': request.form.get('email', '').strip().lower(),
        'password': request.form.get('password', ''),
        'confirmar_password': request.form.get('confirmar_password', '')
    }

    if not Usuario.validar_registro(data):
        return redirect('/')

    data['password'] = bcrypt.generate_password_hash(
        data['password']
    ).decode('utf-8')

    usuario_id = Usuario.save(data)

    if not usuario_id:
        flash('Error al registrar el usuario', 'error')
        return redirect('/')

    session['usuario_id'] = usuario_id
    session['nombre'] = data['nombre']

    return redirect('/dashboard')


# Iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    usuario = Usuario.get_by_email({'email': email})

    if not usuario:
        flash('Correo o contraseña incorrectos', 'error')
        return redirect('/')

    if not bcrypt.check_password_hash(usuario.password, password):
        flash('Correo o contraseña incorrectos', 'error')
        return redirect('/')

    session['usuario_id'] = usuario.id
    session['nombre'] = usuario.nombre

    return redirect('/dashboard')


# Cerrar sesión
@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    return redirect('/')