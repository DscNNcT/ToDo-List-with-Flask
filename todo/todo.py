from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort #En caso de que un usuario intente actualizar un ToDo que no le pertenezca.
# -- Vamos a crear esta función para proteger el endpoint solicitando siempre que exista la sesión del usuario.
from todo.auth import login_required #Crearemos la función apenas terminemos de registrar el blueprint.
from todo.db import get_db

bp = Blueprint('todo', __name__) #Creamos el blueprint de nombre 'todo'.

@bp.route('/') #Este decorador se utiliza para indicar la URL que se debe asociar con la vista. En este caso, la URL es simplemente la raíz del sitio web ("/").
@login_required #Una vez se ingrese en esta ruta, se chequea el inicio de sesión
def index(): #si el inicio de sesión es correcto, se activa la función index que listará los todo del usuario.
    db, c = get_db()
    c.execute(
        'select t.id, t.description, u.username, t.completed, t.created_at from todo t JOIN user u on t.created_by = u.id where t.created_by = %s order by created_at desc',
        #Los elementos consultados (t.id, t.description, u.username, t.completed, t.created_at)
        #deben cumplir con que el created_by en la tabla de todo, sea igual al id en la tabla de user
        #y vendrán ordenados en base a created_at y de forma descendente.
        (g.user['id'],)
    )
    todos = c.fetchall()
    return render_template('todo/index.html', todos = todos) #renderizar una plantilla HTML llamada "index.html" y enviarla como respuesta HTTP al cliente.
    #La plantilla "index.html" es renderizada con los valores pasados a través del diccionario todos = todos. El diccionario todos es pasado como un argumento a la función render_template y contiene la información necesaria para construir la plantilla.

@bp.route('/create', methods=['GET', 'POST']) #Creamos la ruta y asignamos los métodos.
@login_required #solicitamos que se cumpla login_required.
def create(): #definimos la función create.
    if request.method == 'POST': #verificamos que se esté usando metodo post
        description =  request.form['description'] # Tomamos la descripción desde request.form
        error = None #creamos un mensaje de error inofensivo.

        if not description: #Si la descripción no se ingresó
            error = 'Descripción es requerida' #Le indicamos al usuario el error.
        if error is not None: #Verificamos un cambio en error.
            flash(error) #Flasheamos un error
        else: #Si no hay error finalmente procedemos.
            db, c = get_db() # Obtenemos la bbdd y el cursor
            c.execute(
                #Ejecutamos un codigo SQL en la bbdd para insertar datos en la bbdd "todo".
                'insert into todo (description, completed, created_by)'
                'values (%s, %s, %s)',
                #Insertamos description como el input del usuario, false para indicar que la completitud sea 0, y g.user['id'] para identificar a quien corresponde el ToDo.
                (description, False, g.user['id'])
            )
            db.commit() #Comprometemos la bbdd.
            return redirect(url_for('todo.index')) #Redireccionamos al usuario a su pagina principal donde se muestran los ToDo (index).
    return render_template('todo/create.html') #Asignamos la renderización de una plantilla en create.html

#Para esta edición vamos a indicar cual va a ser el ToDo que queremos actualizar.
# para esto primero indicamos que el id es un dato de tipo int.
def get_todo(id): #Definimos esta función para obtener el id del ToDo que vamos a editar.
#Recordemos que el id se lo estamos entregando a la función a través de la plantilla de index a la hora de seleccionar editar el ToDo.
    db, c = get_db() #Traemos nuestra base de datos y cursor.
    c.execute(
        #solicitamos los valores de id, descripción, completitud, autor y fecha de creación desde la tabla todo
        #Siempre y cuando el created_by corresponda al user id de quien inició la sesión.
        'select t.id, t.description, t.completed, t.created_by, t.created_at, u.username from todo t join user u on t.created_by = u.id where t.id = %s',
        (id,)
    )
    todo = c.fetchone() #lanza el primer dato que encuentra.

    if todo is None:
        abort(404, "El ToDo de id{0} no existe".format(id)) #Caso en que no exista un todo para el id.
    
    return todo

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    todo = get_todo(id) #Definimos el todo que vamos a editar

    if request.method == 'POST': #Verificamos que se este usando el metodo post
        description = request.form['description'] #guardamos la descripción
        completed = True if request.form.get('completed') == 'on' else False #Guardamos un valor booleano para el checkbox de completitud.
        error = None #creamos nuestra variable de error

        if not description: #Si description se encuentra vacío
            error = "La descripción es requerida."
        
        if error is not None: #Si descripción contiene un error
            flash(error)
        
        else: #Si no tenemos errores:
            db, c = get_db() #vamos a buscar a la bbdd y al cursor
            c.execute( #ejecutamos la actualización del ToDo
                'update todo set description = %s, completed = %s where id = %s and created_by = %s',
                #Le entregamos un nuevo valor a description, completed para cuando se cumpla que el id sea igual al que tenemos almacenado.
                (description, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', todo = todo)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    db, c = get_db()
    c.execute(
        'delete from todo where id = %s and created_by = %s', (id, g.user['id'])
    )
    db.commit()
    return redirect(url_for('todo.index'))