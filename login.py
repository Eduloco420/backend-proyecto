from flask import Blueprint, request, jsonify
from funcion_jwt import write_token, valida_token
from db import get_db

routes_auth = Blueprint("routes_auth", __name__)

@routes_auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    conexion = get_db()
    cursor = conexion.connection.cursor()
    sql = "SELECT * FROM usuario WHERE mailUsuario = %s AND passUsuario = %s "
    cursor.execute(sql, (data['mail'],data['password']))
    resultado = cursor.fetchone()
    if resultado[8] == 0:
        return jsonify({"mensaje":"Usuario bloqueado, favor contactar a soporte"})
    if resultado:
        usuario = { 'id':resultado[0],
                    'rutUsuario':resultado[1],
                    'nomUsuario':resultado[2],
                    'apeUsuario':resultado[3],
                    'mailUsuario':resultado[4],
                    'rolUsuario':resultado[5],
                    'passUsuario':resultado[6],
                    'fecCreacionUsuario':resultado[7].strftime("%Y-%m-%d %H:%M:%S"),
                    'activeUsuario':resultado[8]    }
        return write_token(data=usuario)
    else:
        return jsonify({"mensaje":"Credenciales Incorrectas"})

@routes_auth.route("/verify/token")
def verify_token():
    token = request.headers['Authorization'].split(" ")[1]
    return valida_token(token, output=True)
