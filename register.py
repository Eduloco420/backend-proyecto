from flask import jsonify
from hashed import hash_password

def registrar(con, data):
    rut = data['rut']
    nombre = data['nombre']
    apellido = data['apellido']
    mail = data['mail']
    rol = data['rol']
    password = data['password']

    try:

        hashedPassword = hash_password(password)

        con.connection.begin()
        cursor = con.connection.cursor()
        sql = ('INSERT INTO usuario (rutUsuario, nomUsuario, apeUsuario, mailUsuario, rolUsuario, passUsuario, fecCreacionUsuario, activeUsuario) VALUES (%s, %s, %s, %s, %s, %s, now(), false);')
        cursor.execute(sql, (rut,nombre,apellido,mail,rol,hashedPassword))

        con.connection.commit()
        response = jsonify({'mensaje':'Usuario creado con exito'})
        response.status_code = 200
        return response
    
    except Exception as e:
        con.connection.rollback()
        return jsonify({'mensaje':'Error en la creación de usuario ' + e})
    
#def activarCuenta(con):


