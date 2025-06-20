from flask import jsonify
import os
import uuid
import math

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
    
def editar_categoria(con, data, id):
    nombre = data['nombre'],
    
    cursor = con.connection.cursor()
    sql = "UPDATE categoria SET nomCategoria = %s WHERE id = %s"
    cursor.execute(sql, (nombre, id))
    con.connection.commit()
    cursor.close()
    response = jsonify({'mensaje':'Categoría modificada correctamente'})
    response.status_code = 200
    return response

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

def editar_subcategoria(con, data, id):
    nombre = data['nombre'],
    categoria = data['categoria']
    cursor = con.cursor.cursor()
    sql = "UPDATE subcategoria SET nomsubcategoria = %s, categoria = %s WHERE id = %s"
    cursor.execute(sql, (nombre, categoria, id))
    con.connection.commit()
    cursor.close()
    response = jsonify({'mensaje':'Subcategoria modificada correctamente'})
    response.status_code = 200
    return response
    
def crear_marca(con,data):
    marca = data['marca']
    cursor = con.connection.cursor()
    sql = "INSERT INTO marca (nomMarca) VALUES (%s)"
    cursor.execute(sql, (marca,))
    con.connection.commit()
    marca_id = cursor.lastrowid
    response = jsonify({'mensaje':'Marca creada con exito', 'id':marca_id})
    response.status_code = 200
    return response

def crear_producto(con, data, imagenes, app):
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
            
        sqlOpcion = ('INSERT INTO opcionProducto (producto, glosaOpcion, opcionActiva) VALUES (%s,%s,1)')
        sqlStock = ('INSERT INTO inventario (producto, stock, sucursal) VALUES (%s,%s,%s)')
        sqlImagen = ('INSERT INTO imagenproducto (producto, imagen) VALUES (%s, %s)')

        for i in stock:
            cursor.execute(sqlOpcion, (producto_id, i['opcion']))
            opcion_id = cursor.lastrowid
            for c in i['cantidad']:
                cantidad_valor = c.get('cant')  
                cursor.execute(sqlStock, (opcion_id, cantidad_valor, c['sucursal']))

        rutas_imagenes = []
            
        for img in imagenes:
            if img.filename != '':
                ext = os.path.splitext(img.filename)[1]
                nombreArchivo = f"{producto_id}_{uuid.uuid4().hex}{ext}"
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombreArchivo)
                img.save(ruta)
                rutas_imagenes.append(ruta)
                cursor.execute(sqlImagen, (producto_id, nombreArchivo))

        con.connection.commit()
        cursor.close()

        response = jsonify({'mensaje':'Producto creado con exito'})
        response.status_code = 200
        return response
    except Exception as e:
        con.connection.rollback()
        return jsonify({'mensaje':f"Error al insertar producto: {e}"})
    
def lista_productos(con, pagina, categoria, subcategoria,search):
    cant_prod = 12
    offset = (pagina - 1) * cant_prod
    cursor = con.connection.cursor()
    if categoria:
        cursor.execute("SELECT count(idProducto) FROM v_producto_lista where idcategoria = %s", (categoria, ))
        total_prod = cursor.fetchone()[0]
        total_pag = int(math.ceil(total_prod/cant_prod))
        sql = 'SELECT * FROM v_producto_lista WHERE idcategoria = %s LIMIT %s OFFSET %s'
        cursor.execute(sql, (categoria, cant_prod, offset))
    elif subcategoria:
        cursor.execute("SELECT count(idProducto) FROM v_producto_lista where idsubcategoria = %s", (subcategoria, ))
        total_prod = cursor.fetchone()[0]
        total_pag = int(math.ceil(total_prod/cant_prod))
        sql = 'SELECT * FROM v_producto_lista WHERE idsubcategoria = %s LIMIT %s OFFSET %s'
        cursor.execute(sql, (subcategoria, cant_prod, offset))
    elif search:
        cursor.execute("SELECT count(idProducto) FROM v_producto_lista where LOWER(nomProducto) like %s", (f"%{search.lower()}%", ))
        total_prod = cursor.fetchone()[0]
        total_pag = int(math.ceil(total_prod/cant_prod))
        sql = 'SELECT * FROM v_producto_lista where LOWER(nomProducto) like %s LIMIT %s OFFSET %s'
        cursor.execute(sql, (f"%{search.lower()}%", cant_prod, offset))
    else:    
        sql = 'SELECT * FROM v_producto_lista'
        cursor.execute(sql)
        total_pag = 0
        pagina = 0 
    datos = cursor.fetchall()
    productos = []
    for i in datos:
        producto = {'idProducto':i[0],
                    'nomProducto':i[1],
                    'idCategoria':i[2],
                    'idMarca':i[3],
                    'idSubCategoria':i[4],
                    'nomCategoria':i[5],
                    'nomSubCategoria':i[6],
                    'nomMarca':i[7],
                    'valorOriginal':i[8],
                    'valorOferta':i[9],
                    'imagen':i[10],
                    'despacho':i[11],
                    'retiro':i[12],
                    'cantidadOpciones':i[13]}  #Agregué esto para poder saber si mostrar botón "Agregar al Carrito o "Ver Opciones" 
        print(f"Producto {i[0]} tiene {i[13]} opciones")            
        productos.append(producto)
    response = jsonify({'mensaje':'Listado Extraido correctamente',
                        'paginaActual': pagina,
                        'paginasTotal': total_pag,
                        'Productos':productos})
    response.status_code = 200
    return response

def lista_productos_ofertas(con, pagina):
    cant_prod = 12
    offset = (pagina - 1) * cant_prod
    cursor = con.connection.cursor()
    
    # Solo productos donde valorOferta IS NOT NULL y es menor que valorOriginal
    cursor.execute("SELECT count(idProducto) FROM v_producto_lista WHERE valorOferta IS NOT NULL AND valorOferta < valorOriginal")
    total_prod = cursor.fetchone()[0]
    total_pag = int(math.ceil(total_prod/cant_prod))
    
    sql = 'SELECT * FROM v_producto_lista WHERE valorOferta IS NOT NULL AND valorOferta < valorOriginal LIMIT %s OFFSET %s'
    cursor.execute(sql, (cant_prod, offset))
    
    datos = cursor.fetchall()
    productos = []
    for i in datos:
        producto = {'idProducto':i[0],
                    'nomProducto':i[1],
                    'idCategoria':i[2],
                    'idMarca':i[3],
                    'idSubCategoria':i[4],
                    'nomCategoria':i[5],
                    'nomSubCategoria':i[6],
                    'nomMarca':i[7],
                    'valorOriginal':i[8],
                    'valorOferta':i[9],
                    'imagen':i[10],
                    'despacho':i[11],
                    'retiro':i[12],
                    'cantidadOpciones':i[13]}
        productos.append(producto)
        
    response = jsonify({'mensaje':'Ofertas obtenidas correctamente',
                        'paginaActual': pagina,
                        'paginasTotal': total_pag,
                        'Productos':productos})
    response.status_code = 200
    return response

def ver_producto(con, prod):
    cursor = con.connection.cursor()
    sqlProducto = "SELECT * FROM v_detalle_producto_1 WHERE id = %s"
    cursor.execute(sqlProducto, (prod, ))
    productoData = cursor.fetchone()

    sqlEspec = "SELECT * FROM v_detalle_producto_2 WHERE producto = %s"
    cursor.execute(sqlEspec, (prod, ))
    especData = cursor.fetchall()
    especs = []

    for e in especData:
        espec = {'nomEspecificacion':e[1],
                 'valorEspecificacion':e[2]}
        especs.append(espec)

    sqlStock = 'SELECT * FROM v_detalle_producto_3 WHERE producto = %s'
    cursor.execute(sqlStock, (prod,))
    stockData = cursor.fetchall()
    stocks = []

    """
    for s in stockData:
        stock = {'glosaOpcion':s[2],
                 'cantStock':s[3]}
        stocks.append(stock)
    """
    for s in stockData:
        stock = {'idOpcion': s[0], # <-- FALTABA AGREGAR ESTA LÍNEA, para que el cliente pueda elegir una opcion
                'glosaOpcion':s[2],
                'cantStock':s[3]}
        stocks.append(stock)
        
    sqlImagen = 'SELECT imagen FROM imagenproducto WHERE producto = %s'
    cursor.execute(sqlImagen, (prod, ))
    imagenData = cursor.fetchall()
    imagenes = []

    for i in imagenData:
        imagen = {'imagen':i[0]}
        imagenes.append(imagen) 
    
    # Consulta para obtener precio
    sqlPrecio = """
    SELECT valorProducto 
    FROM valorProducto 
    WHERE producto = %s
    ORDER BY fecInicVigValor DESC
    LIMIT 1
    """
    cursor.execute(sqlPrecio, (prod,))
    precioData = cursor.fetchone()
    precio = precioData[0] if precioData else None

    producto = {'id':productoData[0],
                'nombre':productoData[1],
                'descripcion':productoData[2],
                'subcategoriaId':productoData[3],
                'subcategoria':productoData[4],
                'categoriaId':productoData[5],
                'categoria':productoData[6],
                'marcaId':productoData[7],
                'marca':productoData[8],
                'despacho':bool(productoData[9]),
                'retiro':bool(productoData[10]),
                'opcion': productoData[11],
                'precio': precio,
                'especificaciones': especs,
                'stock': stocks,
                'imagenes': imagenes
            }
    response = jsonify({'mensaje':'Ok', 'producto':producto})
    response.status_code = 200
    return response

def lista_subcategoria(con):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM v_subcategorias"
    cursor.execute(sql)
    datos = cursor.fetchall()
    subcategorias = []
    for d in datos:
        subcategoria = {'id':d[0],
                        'nombre':d[1],
                        'categoria':d[2],
                        'categoriaNom':d[3]}
        subcategorias.append(subcategoria)
    response = jsonify({'mensaje':'Datos conseguidos correctamente','subcategorias':subcategorias})
    response.status_code = 200
    return response        
    
def lista_categoria(con):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM categoria"
    cursor.execute(sql)
    datos = cursor.fetchall()
    categorias = []
    for d in datos:
        categoria = {'id':d[0],
                        'nombre':d[1]}
        categorias.append(categoria)
    response = jsonify({'mensaje':'Datos conseguidos correctamente','categoria':categorias})
    response.status_code = 200
    return response   

def lista_marcas(con):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM marca"
    cursor.execute(sql)
    datos = cursor.fetchall()
    marcas = []
    for d in datos:
        marca = {'id':d[0],
                 'nombre':d[1]}
        marcas.append(marca)
    response = jsonify({'mensaje':'Datos conseguidos correctamente', 'marcas':marcas})
    response.status_code = 200
    return response