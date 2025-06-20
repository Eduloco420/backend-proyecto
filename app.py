from flask import Flask, jsonify, request, send_from_directory
from flask_mysqldb import MySQL
from config import config
from dotenv import load_dotenv
from login import routes_auth
from db import app, get_db
import producto, sucursal, ventas
from register import registrar, recuperar_contraseña, cambiar_contraseña, ver_usuario, actualizar_user, activar_usuario
import json
from flask_cors import CORS

app.register_blueprint(routes_auth)
conexion = get_db()

CORS(app)

@app.route('/prueba', methods=['GET'])
def prueba(): 
    cursor = conexion.connection.cursor()
    sql = 'SELECT * FROM comuna'
    cursor.execute(sql)
    datos = cursor.fetchall()
    comunas = []
    for fila in datos:
        comuna = {'id':fila[0],
                'nombreComuna':fila[1],
                'provincia':fila[2]}
        comunas.append(comuna)
    return jsonify({'comunas':comunas, 'mensaje':'Consula OK'})    

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return registrar(conexion, data)

@app.route('/producto/categoria', methods=['POST'])
def post_categoria():
    data = request.get_json()
    return producto.crear_categoria(conexion, data)

@app.route('/producto/categoria/<int:id>', methods=['PUT'])
def put_categoria(id):
    data = request.get_json()
    return producto.editar_categoria(conexion, data, id)

@app.route('/producto/categoria', methods=['GET'])
def get_categoria():
    return producto.lista_categoria(conexion)

@app.route('/producto/subcategoria', methods=['POST'])
def post_subcategoria():
    data = request.get_json()
    return producto.crear_subcategoria(conexion, data)

@app.route('/producto/subcategoria/<int:id>', methods=['PUT'])
def put_subcategoria(id):
    data = request.get_json()
    return producto.editar_subcategoria(conexion, data, id)

@app.route('/producto/subcategoria', methods=['GET'])
def get_subcategoria():
    return producto.lista_subcategoria(conexion)

@app.route('/producto/marca', methods=['POST'])
def post_marca():
    data = request.get_json()
    return producto.crear_marca(conexion, data)

@app.route('/sucursal', methods=['POST'])
def post_sucursal():
    data = request.get_json()
    return sucursal.crear_sucursal(conexion, data)

@app.route('/sucursal', methods=['GET'])
def get_sucursal():
    return sucursal.lista_sucursales(conexion)

@app.route('/producto', methods=['POST'])
def post_producto():
    data = request.form.get('data')
    if not data:
        return jsonify({"error": "No se recibió el JSON"}), 400
    
    data = json.loads(data)  

    imagenes = request.files.getlist('imagenes')

    return producto.crear_producto(conexion, data, imagenes, app)

@app.route('/producto', methods=['GET'])
def get_producto():
    pagina = int(request.args.get('pagina', 1))
    categoria = request.args.get('categoria')
    subcategoria = request.args.get('subcategoria')
    search = request.args.get('search')
    return producto.lista_productos(conexion, pagina, categoria, subcategoria,search)

# NUEVO! lo puse para poder mostrar productos en Oferta - KARLA
@app.route('/producto/ofertas', methods=['GET'])
def get_ofertas():
    pagina = int(request.args.get('pagina', 1))
    return producto.lista_productos_ofertas(conexion, pagina)

@app.route('/producto/<producto_id>', methods=['GET'])
def get_detalle(producto_id):
    return producto.ver_producto(conexion, producto_id)

@app.route('/venta', methods=['POST'])
def post_venta():
    data = request.get_json()
    return ventas.ingresar_venta(conexion, data)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# NUEVO-AGREGADO POR KARLA
@app.route('/activar-usuario/<int:id>', methods=['PUT']) 
def activar_usuario(id):
    try:
        cursor = conexion.connection.cursor()
        sql = 'UPDATE usuario SET activeUsuario = 1 WHERE id = %s AND activeUsuario = 0'
        cursor.execute(sql, (id,))
        conexion.connection.commit()
        
        if cursor.rowcount > 0:
            response = jsonify({'mensaje': 'Cuenta activada exitosamente'})
            response.status_code = 200
            return response
        else:
            response = jsonify({'mensaje': 'Usuario no encontrado o ya está activo'})
            response.status_code = 400
            return response
    except Exception as e:
        response = jsonify({'mensaje': 'Error al activar cuenta', 'error': str(e)})
        response.status_code = 500
        return response

@app.route('/recuperar/mail', methods=['POST'])
def mail_contraseña():
    data = request.get_json()
    return recuperar_contraseña(conexion, data)

@app.route('/recuperar/cambiar', methods=['PUT'])
def put_password():
    data = request.get_json()
    return cambiar_contraseña(conexion, data)

@app.route('/usuarios', methods=['GET'])
def get_user():
    rut = request.args.get('rut')
    mail = request.args.get('mail')

    return ver_usuario(conexion, rut, mail)

@app.route('/usuarios/<int:id>', methods=['PUT'])
def put_user(id):
    data = request.get_json()
    return actualizar_user(conexion, data, id)

@app.route('/usuarios/<int:id>', methods=['GET'])
def get_user_by_id(id):
    cursor = conexion.connection.cursor()
    sql = "SELECT id, rutUsuario, nomUsuario, apeUsuario, mailUsuario, rolUsuario, activeUsuario FROM usuario WHERE id = %s"
    cursor.execute(sql, (id,))
    
    datos = cursor.fetchone()
    
    if datos:
        usuario = {
            'id': datos[0],
            'rut': datos[1],
            'nombre': datos[2],
            'apellido': datos[3],
            'mail': datos[4],
            'rol': datos[5],
            'activo': datos[6]
        }
        
        response = jsonify({'mensaje': 'Usuario encontrado', 'usuario': usuario})
        response.status_code = 200
        return response
    else:
        response = jsonify({'mensaje': 'Usuario no encontrado'})
        response.status_code = 404
        return response

@app.route('/producto/marca', methods=['GET'])
def get_marca():
    return producto.lista_marcas(conexion)

@app.route('/usuarios/activar/<int:id>', methods=['PUT'])
def active_user(id):
    return activar_usuario(conexion, id)

@app.route('/pagos/<int:id>', methods=['GET'])
def get_pagos(id):
    return ventas.ver_pagos(conexion, id)

@app.route('/ventas', methods=['GET'])
def get_ventas():
    return ventas.ver_ventas(conexion)

if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True)
