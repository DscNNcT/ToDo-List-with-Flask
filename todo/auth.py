import functools #set de funciones para construir aplicaciones.
from flask import(
    Blueprint, #Nos permite crear blueprints configurables.
    flash, #Funcion que nos permite enviar mensaje de forma generica a nuestras plantillas.
    g, #variable trascendental a la apricación.
    render_template, #renderiza plantillas
    request, #vamos a recibir datos desde un formulario.
    url_for, #vamos a crear urls.
    session, #para poder mantener una referencia del usuario que se encuentra en el contexto actual interactuando con la app.
    redirect
)
from werkzeug.security import (
    check_password_hash, #verifica que la contraseña que se ingresa sea igual a otra.
    generate_password_hash #encripta la contraseña que se está enviando.
)

from todo.db import get_db #importamos esto para poder interactuar con la bbdd.

bp = Blueprint('auth', __name__, url_prefix='/auth') #Es importante registrar este blueprint en la aplicación (__init__.py).

### - Agregamos una ruta de registro dentro de nuestro blueprint
@bp.route('/register', methods=['GET', 'POST']) #ruta /register, metodos que manejará la ruta.
def register():
    if request.method == 'POST': #Primero validamos dentro del request que se está enviando al sv sea el de POST.
        username = request.form['username'] #Vamos a obtener username.
        password = request.form['password'] #Vamos a obtener password.
        db, c = get_db() #Vamos a buscar la base y el cursor.
        error = None #definimos una variable de error para mas adelante usarla como flash.
        c.execute( #Ejecutamos la siguiente consulta a nuestra bbdd
            'select id from user where username = %s', #Esta consulta selecciona el id si el username en user es distinto de None.
            (username,) #Importante agregar el segundo argumento.
        )
# -- Definimos los 3 errores posibles para el registro de un usuario con 2 campos.
    # 1. Que no se registre un username.
        if not username: #Si no tenemos un username de parte del usuario entregamos un mensaje de error.
            error = 'Username es requerido'
    # 2. Que no se registre una password.
        if not password: #Si no tenemos un password de parte del usuario entregamos un mensaje de error.
            error = 'Password es requerido'
    # 3. Que el username registrado ya exista.
        elif c.fetchone() is not None: #Si, por el contrario, tenemos un username, vamos a buscar si existe la coincidencia dentro de la bbdd.
            error = 'Usuario {} ya se encuentra registrado.'.format(username) #Esta sintaix con {} es solo posible si se utiliza el metodo format de los strings.
# -- Validamos que el error no exista para ejecutar el registro.
        if error is None:
            c.execute(
                'insert into user (username, password) values (%s, %s)',
                (username, generate_password_hash(password)) #aquí llamamos el username y la contraseña encriptada con generate_password_hash
            )
            db.commit() #commit para comprometer la bbdd.

            return redirect(url_for('auth.login')) #Una vez que se haya completado el registro enviamos al usuario a auth.login (debemos crear esta entrada)
        
        flash(error) #Si no tuvimos un caso de éxito enviamos mensaje de error.

    return render_template('auth/register.html') #retornamos en caso de que la petición no sea POST sino GET.

### - Agregamos una ruta de login dentro de nuestro blueprint
@bp.route('/login', methods=['GET', 'POST']) #ruta /register, metodos que manejará la ruta.
def login():
    if request.method == 'POST': #Primero validamos dentro del request que se está enviando al sv sea el de POST.
        username = request.form['username'] #Vamos a obtener username.
        password = request.form['password'] #Vamos a obtener password.
        db, c = get_db() #Vamos a buscar la base y el cursor.
        error = None #definimos una variable de error para mas adelante usarla como flash.
        c.execute( #Ejecutamos la siguiente consulta a nuestra bbdd
            'select * from user where username = %s', (username,) #buscamos si existe algun usuario con un username coincidente con lo enviado.
        )
        user = c.fetchone() #definimos la variable user como el registro coincidente de la bbdd con username.
# -- Verificamos errores
    # 1. Si no existe coincidencia en la bbdd.        
        if user is None:
            error = 'Usuario y/o contraseña inválida' #Mensaje ambiguo para evitar obtener datos por la fuerza.
    # 2. Si existe coincidencia de usuario pero no de contraseña.
        elif not check_password_hash(user['password'], password):
            error = 'Usuario y/o contraseña inválida' #Mismo mensaje ambiguo para evitar entregar información específica respecto al error.

# -- En caso de que no exista error
        if error is None:
            session.clear() #Vamos a limpiar la sesión.
            session['user_id'] = user['id'] #creamos variable dentro de la sesión que vamos a llamar user_id, y le pasaremos el id asignado al usuario en la bbdd.
            return redirect(url_for('todo.index')) #redirigimos al usuario a la página de inicio.
        
        flash(error) # Caso en el que el usuario tuvo errores.
    
    return render_template('auth/login.html') #retornamos en caso de que la petición no sea POST sino GET.

### - FUNCION DECORADORA PARA CHEQUEAR EL LOGIN.
    # 1. Primero creamos una función que asigne el usuario dentro de la variable trascendental 'g'.
@bp.before_app_request
def load_logged_in_user(): #definimos la función.
    user_id = session.get('user_id') #vamos a sacar el user_id dentro de nuestro objeto de sesión.

    if user_id is None: #comprobamos si se obtuvo algo desde el objeto de sesión.
        g.user = None #si no se obtuvo nada, dejamos g.user como None.
    else:
        db, c = get_db() #Si existe, vamos a ir a buscar con el user_id el usuario a la bbdd.
        c.execute(
            'select * from user where id = %s', (user_id,) #busca en base al id que guardamos en sesión el registro en la bbdd.
        )
        g.user = c.fetchone() # Guarda en g.user el primer elemento.

    # 2. Definimos la función que protegerá los ToDos requiriendo el login.
def login_required(view):
    @functools.wraps(view) #Envolvemos a la función utilizando la función de wraps.
    def wrapped_view(**kwargs): #
        if g.user is None: #Preguntamos si g.user es None. Si es afirmativo, el usuario no ha iniciado sesión.
            return redirect(url_for('auth.login')) #Redireccionamos al usuario a la pagina de login.
        return view(**kwargs) #Si el usuario inició sesión, vamos a devolver la vista y los argumentos.
    return wrapped_view #Devolvemos la función recién creada.

### - FUNCIÓN DE LOGOUT.
@bp.route('/logout') #Creamos la ruta de logout
def logout():
    session.clear() #limpiamos la sesión del usuario.
    return redirect(url_for('auth.login')) #redirigimos al usuario al login.
