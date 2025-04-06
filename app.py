from flask import Flask, jsonify, request, send_from_directory
from flask_mysqldb import MySQL
from config import config
from dotenv import load_dotenv
from login import routes_auth
from db import app, get_db
import producto, sucursal
from register import registrar
import json

app.register_blueprint(routes_auth)
conexion = get_db()

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

@app.route('/producto/subcategoria', methods=['POST'])
def post_subcategoria():
    data = request.get_json()
    return producto.crear_subcategoria(conexion, data)

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
    return producto.lista_productos(conexion, pagina, categoria, subcategoria)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True)
