
from flask import render_template, redirect, request, session, flash
from models.mision import Mision
from __init__ import app


# Mostrar dashboard
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect('/')

    misiones = Mision.get_all()
    return render_template('dashboard.html', misiones=misiones)


# Formulario para crear misión
@app.route('/nueva')
def nueva():
    if 'usuario_id' not in session:
        return redirect('/')

    return render_template('nueva.html')


# Crear misión
@app.route('/crear_mision', methods=['POST'])
def crear_mision():
    if 'usuario_id' not in session:
        return redirect('/')

    data = {
        'nombre': request.form.get('nombre', '').strip(),
        'fecha': request.form.get('fecha', ''),
        'voluntarios': request.form.get('voluntarios', ''),
        'descripcion': request.form.get('descripcion', '').strip(),
        'usuario_id': session['usuario_id']
    }

    if not Mision.validar_mision(data):
        return redirect('/nueva')

    resultado = Mision.save(data)

    if not resultado:
        flash('Error al crear la misión', 'error')

    return redirect('/dashboard')


# Ver misión
@app.route('/ver/<int:id>')
def ver_mision(id):
    if 'usuario_id' not in session:
        return redirect('/')

    mision = Mision.get_by_id({'id': id})

    if not mision:
        flash('La misión no existe', 'error')
        return redirect('/dashboard')

    voluntarios = Mision.get_voluntarios({'mision_id': id})

    inscrito = Mision.esta_inscrito({
        'usuario_id': session['usuario_id'],
        'mision_id': id
    })

    return render_template(
        'ver.html',
        mision=mision,
        voluntarios=voluntarios,
        inscrito=inscrito
    )


# Inscribirse en una misión
@app.route('/inscribir/<int:id>', methods=['POST'])
def inscribir_mision(id):
    if 'usuario_id' not in session:
        return redirect('/')

    mision = Mision.get_by_id({'id': id})

    if not mision:
        flash('La misión no existe', 'error')
        return redirect('/dashboard')

    data = {
        'usuario_id': session['usuario_id'],
        'mision_id': id
    }

    if Mision.esta_inscrito(data):
        flash('Ya estás inscrito en esta misión', 'error')
        return redirect(f'/ver/{id}')

    voluntarios = Mision.get_voluntarios({'mision_id': id})

    if len(voluntarios) >= int(mision.voluntarios):
        flash('Esta misión ya tiene todos sus voluntarios', 'error')
        return redirect(f'/ver/{id}')

    resultado = Mision.inscribir(data)

    if resultado is False:
        flash('No se pudo realizar la inscripción', 'error')
    else:
        flash('Te inscribiste correctamente', 'success')

    return redirect(f'/ver/{id}')


# Retirarse de una misión
@app.route('/retirar/<int:id>', methods=['POST'])
def retirar_mision(id):
    if 'usuario_id' not in session:
        return redirect('/')

    mision = Mision.get_by_id({'id': id})

    if not mision:
        flash('La misión no existe', 'error')
        return redirect('/dashboard')

    data = {
        'usuario_id': session['usuario_id'],
        'mision_id': id
    }

    if not Mision.esta_inscrito(data):
        flash('No estás inscrito en esta misión', 'error')
        return redirect(f'/ver/{id}')

    resultado = Mision.retirar(data)

    if resultado is False:
        flash('No se pudo retirar la inscripción', 'error')
    else:
        flash('Te retiraste de la misión correctamente', 'success')

    return redirect(f'/ver/{id}')


# Formulario para editar misión
@app.route('/editar/<int:id>')
def editar_mision(id):
    if 'usuario_id' not in session:
        return redirect('/')

    mision = Mision.get_by_id({'id': id})

    if not mision:
        flash('La misión no existe', 'error')
        return redirect('/dashboard')

    if mision.usuario_id != session['usuario_id']:
        flash('No puedes editar esta misión', 'error')
        return redirect('/dashboard')

    return render_template('editar.html', mision=mision)


# Actualizar misión
@app.route('/actualizar_mision/<int:id>', methods=['POST'])
def actualizar_mision(id):
    if 'usuario_id' not in session:
        return redirect('/')

    mision = Mision.get_by_id({'id': id})

    if not mision or mision.usuario_id != session['usuario_id']:
        flash('No tienes permiso para editar esta misión', 'error')
        return redirect('/dashboard')

    data = {
        'id': id,
        'nombre': request.form.get('nombre', '').strip(),
        'fecha': request.form.get('fecha', ''),
        'voluntarios': request.form.get('voluntarios', ''),
        'descripcion': request.form.get('descripcion', '').strip(),
        'usuario_id': session['usuario_id']
    }

    if not Mision.validar_mision(data):
        return redirect(f'/editar/{id}')

    inscritos = Mision.get_voluntarios({'mision_id': id})

    if int(data['voluntarios']) < len(inscritos):
        flash('No puedes reducir los cupos por debajo de los inscritos', 'error')
        return redirect(f'/editar/{id}')

    Mision.update(data)
    return redirect('/dashboard')


# Eliminar misión
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_mision(id):
    if 'usuario_id' not in session:
        return redirect('/')

    mision = Mision.get_by_id({'id': id})

    if not mision or mision.usuario_id != session['usuario_id']:
        flash('No tienes permiso para eliminar esta misión', 'error')
        return redirect('/dashboard')

    Mision.delete({
        'id': id,
        'usuario_id': session['usuario_id']
    })

    return redirect('/dashboard')
