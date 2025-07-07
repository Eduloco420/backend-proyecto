from flask import Blueprint, request, jsonify
from funcion_jwt import write_token, valida_token
from db import get_db
from hashed import check_password

routes_auth = Blueprint("routes_auth", __name__)

@routes_auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    admin_flag = data.get('admin')
    print(data)
    conexion = get_db()
    cursor = conexion.connection.cursor()
    sql = "SELECT * FROM usuario WHERE mailUsuario = %s "
    cursor.execute(sql, (data['mail'],))
    resultado = cursor.fetchone()
    if resultado is None:
        return jsonify({"error": "Usuario no encontrado"}), 401
    if resultado[8] == 0:
        return jsonify({"mensaje":"Usuario bloqueado, favor contactar a soporte"}), 401
    if admin_flag == "1" and resultado[5] == 1:
        print('Usuario sin privilegios')
        return jsonify({'mensaje': 'Usuario sin privilegios' }), 401
    usuario = { 'id':resultado[0],
                'rutUsuario':resultado[1],
                'nomUsuario':resultado[2],
                'apeUsuario':resultado[3],
                'mailUsuario':resultado[4],
                'rolUsuario':resultado[5],
                'passUsuario':resultado[6],
                'fecCreacionUsuario':resultado[7].strftime("%Y-%m-%d %H:%M:%S"),
                'activeUsuario':resultado[8]    }
    if check_password(usuario['passUsuario'],data['password']):
        token = str(write_token(data=usuario)).split("'")[1]
        response = jsonify({'mensaje':'logueado con exito', 'token':token})
        response.status_code = 200
        return response
    else:
        return jsonify({'mensaje':'contraseña incorrecta'}), 401

@routes_auth.route("/verify/token")
def verify_token():
    token = request.headers['Authorization']
    return valida_token(token, output=True)
