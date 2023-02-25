import mysql.connector #importamos el conector de mysql
import click #importamos click para poder para poder ejecutar comandos en la terminal
from flask import current_app, g #current_app mantiene la app que estamos ejecutando
                                #g es una variable que está en toda nuestra app. La usaremos para almacenar el usuario.
from flask.cli import with_appcontext #con appcontext podemos acceder a las variables de la config.
from .schema import instructions #Lo creamos nosotros. Contiene los scripts para poder crear nuestra bbdd.

#Definimos una funcion que nos permita obtener nuestra ddbb y el cursor dentro de nuestra app.
def get_db():
    if 'db' not in g: #Si no se encuentra el atributo 'db' dentro de g
        g.db = mysql.connector.connect( #Vamos a generar una propiedad dentro de g que contendrá la conexión a la bbdd.
            host = current_app.config['DATABASE_HOST'], #Aquí usaremos la propiedad de current_app para definir las credenciales ingresadas en __init__.py
            user = current_app.config['DATABASE_USER'],
            password = current_app.config['DATABASE_PASSWORD'],
            database = current_app.config['DATABASE'],
        )
        g.c = g.db.cursor(dictionary = True) #agregamos la obtención del cursor con acceso a las propiedades en forma de diccionario
    
    return g.db, g.c #Así al llamar a get_db() vamos a obtener la bbdd y el cursor.

#Definimos ahora una función que nos cierre la conexión de la bbdd cada vez que se realice una petición.
#La idea es que no debemos dejar esa conexión abierta con cada llamado.
def close_db(e = None): 
    db = g.pop('db', None) #se encarga de obtener la variable db del objeto g que es un objeto global que se utiliza para almacenar variables compartidas en una aplicación web Flask.
    #La función pop() busca la clave db en el diccionario g. Si se encuentra la clave db, se devuelve su valor y se elimina la clave db del diccionario g. Si la clave db no se encuentra en el diccionario g, se devuelve el valor predeterminado None.
    if db is not None: #Luego, si db no es None, la función close() se llama en el objeto db para cerrar la conexión de la base de datos.
        db.close()
    
#Creamos una función para añadir la configuración que cierra la conexión al terminar de realizar la petición.
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

#Creamos la función que nos permitirá ejecutar instrucciones en la linea de comandos con objetivo de crear tablas.
def init_db(): # Esta función se encargará de la lógica.
    db, c = get_db() #Aquí llamamos a la base de datos y al cursor.
    
    #Las instrucciones que vamos a importar desde nuestro archivo schema deben estar en una lista y escritas en el orden correcto de ejecución.
    for i in instructions: #iteramos por cada elemento de la lista instructions en schema.
        c.execute(i) #Ejecutando cada elemento de la lista como instrucción.
    db.commit()

@click.command('init-db') #Definimos el nombre que tendrá la instrucción en la línea de comandos para ejecutar esta función. Ej. "Flask init-db" en la cmd ejecutará la función.
@with_appcontext #Esto indicará que se utilice el contexto de la aplicación para que pueda acceder a las variables de config en g.db.

def init_db_command():
    init_db() #Esta funcion se hará cargo de la lógica para correr los scripts que definamos.
    click.echo('Base de datos inicializada') #para indicarnos que nuestro script ha acabado de correr con éxito.