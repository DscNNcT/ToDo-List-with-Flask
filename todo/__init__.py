import os # (operative system) usamos esta libreria para acceder a las variables de entorno.
from flask import Flask #importamos flask.

#para trabajar con esta separacion de modulos debemos crear la funcion create_app.
def create_app(): #servirá para hacer testing o para crear instancias de la app.
    app = Flask(__name__) #Toda aplicación creada en Flask es una instancia de la clase Flask.

#Configuramos nuestra aplicación.
    app.config.from_mapping( #Vamos a definir variables de configuracion con from_mapping.
        SECRET_KEY = 'mikey', #Llave(cookie) a utilizar para definir las sesiones.
    #definimos el host, password, user y ddbb a partir de variables de entorno.
        DATABASE_HOST = os.environ.get('FLASK_DATABASE_HOST'), 
        DATABASE_PASSWORD = os.environ.get('FLASK_DATABASE_PASSWORD'), #
        DATABASE_USER = os.environ.get('FLASK_DATABASE_USER'),
        DATABASE = os.environ.get('FLASK_DATABASE'),
    )

#Llamamos al archivo de bd.py para añadir la configuración de cierre de conexión.
    from . import db #El punto representa el directorio actual, y se utiliza para especificar la ruta relativa al archivo de origen actual.
    db.init_app(app) #Desde el directorio actual estoy importando db.py y llamando a la función init_app.

#Inscribimos el blueprint creado en auth.py en la aplicación.
    from . import auth
    app.register_blueprint(auth.bp) #bp es el nombre que le dimos a la variable blueprint creada en auth.py

#Inscribimos el blueprint de todo.
    from . import todo
    app.register_blueprint(todo.bp)
    
#Creamos una ruta de pruebas.
    @app.route('/hola')
    def hola():
        return 'chanchito feliz'
    
    return app