instructions = [ #Cada string será una instrucción/ elemento de la lista.
    'SET FOREIGN_KEY_CHECKS = 0;', #IMPORTANTE: Si queremos eliminar una tabla, no nos va a dejar si existen referencias de llaves foráneas, por lo que con esta instrucción desactivamos dicha validación.
    'DROP TABLE IF EXISTS todo;', #Si la tabla existe, se elimina y se recrea.
    'DROP TABLE IF EXISTS user;', #Si la tabla existe, se elimina y se recrea.
    'SET FOREIGN_KEY_CHECKS = 1;', #Aquí volvemos a activar la validación de llaves foráneas referenciadas.
    #Con triple comilla doble se crea un string de multiples líneas.
    # -- Primero creo mi tabla de usuario.
    """ 
        CREATE TABLE user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(150) NOT NULL
        );
    """,
    # -- Ahora creo mi tabla de todo.
    """
        CREATE TABLE todo (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_by INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            FOREIGN KEY (created_by) REFERENCES user (id)
        );    
    """

]