from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_mysqldb import MySQL
from config import config
from dotenv import load_dotenv
from login import routes_auth
from db import app, get_db
import producto, sucursal, ventas, direccion, tienda
from register import registrar, recuperar_contraseña, cambiar_contraseña, ver_usuario, actualizar_user, activar_usuario
import json
from flask_cors import CORS
import os
import cloudinary

app.register_blueprint(routes_auth)
conexion = get_db()

cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

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
    categoria = request.args.get('categoria', type=int)
    if categoria is not None:
        return producto.subcat_por_cat(conexion, categoria)
    else:
        return producto.lista_subcategoria(conexion)

@app.route('/producto/marca', methods=['POST'])
def post_marca():
    data = request.get_json()
    return producto.crear_marca(conexion, data)

@app.route('/sucursal', methods=['POST'])
def post_sucursal():
    data = request.get_json()
    return sucursal.crear_sucursal(conexion, data)

@app.route('/ubicaciones', methods=['GET'])
def get_ubicaciones():
    return direccion.obtener_ubicaciones(conexion)

@app.route('/sucursal', methods=['GET'])
def get_sucursales():
    todos = request.args.get('todos')
    return sucursal.lista_sucursales(conexion, todos)

@app.route('/sucursal/<int:id>', methods=['PUT'])
def put_sucursal(id):
    data = request.get_json()
    return sucursal.editar_sucursal(conexion, data, id)

@app.route('/sucursal/<int:id>', methods=['GET'])
def get_sucursal(id):
    return sucursal.buscar_sucursal(conexion, id)

@app.route('/producto', methods=['POST'])
def post_producto():
    data = request.form.get('data')
    if not data:
        return jsonify({"error": "No se recibió el JSON"}), 400
    
    data = json.loads(data)  

    imagenes = request.files.getlist('imagenes')

    return producto.crear_producto(conexion, data, imagenes, app)

@app.route('/producto/especificacion/<int:id>', methods=['DELETE'])
def delete_especificacion(id):
    return producto.eliminar_especificacion(conexion, id)

@app.route('/producto/especificacion', methods=['POST'])
def post_especificacion():
    especs = request.get_json()
    return producto.editar_especificacion(conexion, especs)

@app.route('/producto/opciones', methods=['POST'])
def post_stock():
    opciones = request.get_json()
    return producto.editar_opciones(conexion, opciones)

@app.route('/producto/<int:id>', methods=['PUT'])
def put_producto(id):
    data = request.form.get('data')
    data = json.loads(data)
    imagen = request.files.getlist('imagenes')
    return producto.editar_producto(conexion, data, imagen, id)

@app.route('/producto', methods=['GET'])
def get_producto():
    pagina = int(request.args.get('pagina', 1))
    categoria = request.args.get('categoria')
    subcategoria = request.args.get('subcategoria')
    search = request.args.get('search')
    return producto.lista_productos(conexion, pagina, categoria, subcategoria,search)

@app.route('/producto/detalle/<int:id>', methods=['GET'])
def get_detalle_producto(id):
    return producto.ver_detalle_producto(conexion, id)

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

@app.route('/uploads/<string:nombre_archivo>')
def uploaded_file(nombre_archivo):
    public_id_sin_extension = nombre_archivo.rsplit('.', 1)[0]
    public_id_completo = f"productos/{public_id_sin_extension}"
    url = cloudinary.CloudinaryImage(public_id_completo).build_url(secure=True, force_version=False)
    return redirect(url)

@app.route('/uploads/<int:id>', methods=['DELETE'])
def delete_file(id):
    return producto.eliminar_imagen(conexion, id)

@app.route('/subir_imagenes', methods=['POST'])
def subir_imagenes():
    if 'imagenes' not in request.files:
        return jsonify({'error': 'No se encontraron archivos con key "imagenes"'}), 400

    archivos = request.files.getlist('imagenes')
    resultados = []

    for archivo in archivos:
        if archivo.filename == '':
            continue

        result = cloudinary.uploader.upload(
            archivo,
            folder="productos"  # o el folder que uses
        )

        resultados.append({
            'public_id': result['public_id'],
            'secure_url': result['secure_url'],
            'format': result['format'],
            'version': result['version']
        })

    return jsonify({'imagenes_subidas': resultados}), 200


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
    search = request.args.get('search')
    if search is not None:
        print('busqueda')
        return producto.buscar_marca(conexion, search)
    return producto.lista_marcas(conexion)

@app.route('/usuarios/activar/<int:id>', methods=['PUT'])
def active_user(id):
    return activar_usuario(conexion, id)

@app.route('/ventas', methods=['GET'])
def get_ventas():
    return ventas.ver_ventas(conexion)

@app.route('/ventas/<int:id>', methods=['GET'])
def get_detalle_venta(id):
    return ventas.detalle_venta(conexion, id)

@app.route('/region', methods=['GET'])
def get_region():
    return direccion.obtener_region(conexion)

@app.route('/provincia', methods=['GET'])
def get_provincia():
    region = request.args.get('region')
    return direccion.obtener_provincia(conexion, region)

@app.route('/comuna', methods=['GET'])
def get_comuna():
    provincia = request.args.get('provincia')
    return direccion.obtener_comuna(conexion, provincia)

@app.route('/tienda', methods=['GET'])
def get_tienda():
    return tienda.obtener_tienda(conexion)

@app.route('/tienda', methods=['PUT'])
def put_tienda():
    data = request.get_json()
    return tienda.editar_tienda(conexion, data)

if __name__ == '__main__':
    load_dotenv()  
    
    debug_mode = os.getenv('DEBUG', 'False') == 'True'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
