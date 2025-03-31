from flask import jsonify

def crear_categoria(con, data):
    categoria = data['categoria']
    cursor = con.connection.cursor()
    sql = "INSERT INTO categoria (nomCategoria) VALUES (%s)"
    cursor.execute(sql, (categoria,))
    con.connection.commit()
    response = jsonify({'mensaje':'Categoria creada con exito'})
    response.status_code = 200
    return response

def eliminar_categoria(con, categoria):
    cursor = con.connection.cursor()

def crear_subcategoria(con, data):
    subcategoria = data['subcategoria']
    categoria = data['categoria']
    cursor = con.connection.cursor()
    sql = "INSERT INTO subcategoria (nomSubCategoria, categoria) VALUES (%s, %s)"
    cursor.execute(sql, (subcategoria,categoria))
    con.connection.commit()
    response = jsonify({'mensaje':'Subcategoria creada con exito'})
    response.status_code = 200
    return response
    
def crear_marca(con,data):
    marca = data['marca']
    cursor = con.connection.cursor()
    sql = "INSERT INTO marca (nomMarca) VALUES (%s)"
    cursor.execute(sql, (marca,))
    con.connection.commit()
    response = jsonify({'mensaje':'Marca creada con exito'})
    response.status_code = 200
    return response

def crear_producto(con, data):
    nom_producto = data['nomProducto']
    desc_producto = data['descProducto']
    subcategoria = data['subCategoria']
    marca = data['marca']
    especificaciones = data['especificaciones']
    stock = data['stock']
    opcion = data['opcion']
    retiro_sucursal = data['retiroSucursal']
    despacho_domicilio = data['despachoDomicilio']
    precio = data['precio']
    
    try:
        con.connection.begin()
        cursor = con.connection.cursor()
        sql = ('INSERT INTO productos (nomProducto, descProducto, subCatProducto, marcaProducto, opcion, retiroSucursal, despachoDomicilio) VALUES (%s,%s,%s,%s,%s,%s,%s)')
        cursor.execute(sql, (nom_producto, desc_producto, subcategoria, marca, opcion, retiro_sucursal, despacho_domicilio))
        
        producto_id = cursor.lastrowid

        sql = ('INSERT INTO valorProducto (producto, valorProducto, fecInicVigValor) VALUES (%s,%s, now() )')
        cursor.execute(sql, (producto_id, precio))

        sql = ('INSERT INTO especificacionProducto (producto, nombreEspecificacion, valorEspecificacion) VALUES (%s,%s,%s)')
        for i in especificaciones:
            cursor.execute(sql, (producto_id, i['nombre'], i['valor']))
            
        sqlOpcion = ('INSERT INTO opcionProducto (producto, glosaOpcion) VALUES (%s,%s)')
        sqlStock = ('INSERT INTO inventario (producto, stock, sucursal) VALUES (%s,%s,%s)')
        for i in stock:
            cursor.execute(sqlOpcion, (producto_id, i['opcion']))
            opcion_id = cursor.lastrowid
            cursor.execute(sqlStock, (opcion_id, i['cantidad'], i['sucursal']))

        con.connection.commit()
        cursor.close()

        response = jsonify({'mensaje':'Producto creado con exito'})    
        response.status_code = 200
        return response
    except Exception as e:
        con.connection.rollback()
        return jsonify({'mensaje':f"Error al insertar producto: {e}"})




