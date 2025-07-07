from flask import jsonify
import os
import uuid
import math
import cloudinary.uploader

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
    sql = "INSERT INTO subCategoria (nomSubCategoria, categoria) VALUES (%s, %s)"
    cursor.execute(sql, (subcategoria,categoria))
    con.connection.commit()
    response = jsonify({'mensaje':'Subcategoria creada con exito'})
    response.status_code = 200
    return response

def editar_subcategoria(con, data, id):
    nombre = data['subcategoria'],
    categoria = data['categoria']
    cursor = con.connection.cursor()
    sql = "UPDATE subCategoria SET nomSubCategoria = %s, categoria = %s WHERE id = %s"
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
    marca_info = data['marca']
    especificaciones = data['especificaciones']
    stock = data['stock']
    opcion = data['opcion']
    retiro_sucursal = data['retiroSucursal']
    despacho_domicilio = data['despachoDomicilio']
    precio = data['precio']
    
    try:
        cursor = con.connection.cursor()

        if marca_info['nueva']:
            nombre = marca_info['nombre']
            sql_marca = 'INSERT INTO marca (nomMarca) VALUES (%s)'
            cursor.execute(sql_marca, (nombre,))
            marca = cursor.lastrowid
        else:
            marca = marca_info['id']

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
        sqlImagen = ('INSERT INTO imagenProducto (producto, imagen) VALUES (%s, %s)')

        for i in stock:
            cursor.execute(sqlOpcion, (producto_id, i['opcion']))
            opcion_id = cursor.lastrowid
            for c in i['cantidad']:
                cantidad_valor = c.get('cant')
                cursor.execute(sqlStock, (opcion_id, cantidad_valor, c['sucursal']))
            
        for img in imagenes:
            if img.filename != '':
                result = cloudinary.uploader.upload(
                    img,
                    folder="productos",
                    public_id=f"{producto_id}_{uuid.uuid4().hex}"
                )

                public_id_completo = result['public_id']  # productos/46_abc123xyz
                formato = result['format']                # webp

                # Ahora extraemos sólo el nombre sin el folder
                nombre_sin_folder = public_id_completo.split('/')[-1]  # 46_abc123xyz

                nombre_archivo = f"{nombre_sin_folder}.{formato}"  # 46_abc123xyz.webp

                cursor.execute(sqlImagen, (producto_id, nombre_archivo))

        con.connection.commit()
        cursor.close()

        response = jsonify({'mensaje':'Producto creado con exito'})
        response.status_code = 200
        return response
    except Exception as e:
        con.connection.rollback()
        return jsonify({'mensaje':f"Error al insertar producto: {e}"}), 500
    
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
        cursor.execute("SELECT count(idProducto) FROM v_producto_lista")
        total_prod = cursor.fetchone()[0]
        sql = 'SELECT * FROM v_producto_lista LIMIT %s OFFSET %s'
        cursor.execute(sql, (cant_prod, offset))
        total_pag = int(math.ceil(total_prod/cant_prod))
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
        
    sqlImagen = 'SELECT imagen FROM imagenProducto WHERE producto = %s'
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

def subcat_por_cat(con, categoria):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM subCategoria WHERE categoria = %s"
    cursor.execute(sql, (categoria,))
    datos = cursor.fetchall()
    subcategorias = []
    for d in datos:
        subcategoria = {
            'id':d[0],
            'nombre':d[1],
            'categoria':d[2]
        }
        subcategorias.append(subcategoria)

    return subcategorias            

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

def buscar_marca(con, search):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM marca WHERE nomMarca like %s"
    cursor.execute(sql, (f'{search}%', ))
    datos = cursor.fetchall()
    marcas = []
    for d in datos:
        marca = {'id':d[0],
                 'nombre':d[1]}
        marcas.append(marca)
    return marcas

def ver_detalle_producto(con, id):
    cursor = con.connection.cursor()
    sql_producto = "SELECT * FROM v_detalle_producto WHERE id = %s"
    cursor.execute(sql_producto, (id,))
    prod_datos = cursor.fetchone()

    sql_imagen = "SELECT id, imagen FROM imagenProducto WHERE producto = %s"
    cursor.execute(sql_imagen, (id,))
    img_datos = cursor.fetchall()
    imagenes = []
    for img in img_datos:
        imagenes.append({
            'id':img[0],
            'imagen':img[1]
        })

    sql_valor = "SELECT * FROM valorProducto WHERE producto = %s"
    cursor.execute(sql_valor, (id,))
    valor_datos = cursor.fetchall()
    precios = []
    for valor in valor_datos:
        precios.append({
            'id':valor[0],
            'valorProducto':valor[2],
            'fecInicioVig':valor[3]
        })

    sql_espec = "SELECT id, nombreEspecificacion, valorEspecificacion FROM especificacionProducto WHERE producto = %s"
    cursor.execute(sql_espec, (id,))
    espec_datos = cursor.fetchall()
    especificaciones = []
    for espec in espec_datos:
        especificaciones.append({
            'id':espec[0],
            'nombre':espec[1],
            'valor':espec[2]
        })
    
    sql_stock = "SELECT * FROM v_detalle_stock WHERE producto = %s"
    cursor.execute(sql_stock, (id,))
    stock_datos = cursor.fetchall()
    stock = []
    for st in stock_datos:
        stock.append({
            'id':st[0],
            'glosaOpcion':st[2],
            'opcionActiva':st[3],
            'cantidad':st[4],
            'idSucursal':st[5],
            'nomSucursal':st[6]
        })

    sql_descuento = "SELECT * FROM descuentoProducto where producto = %s"
    cursor.execute(sql_descuento, (id,))
    descuentos_datos = cursor.fetchall()
    descuentos = []
    for dd in descuentos_datos:
        descuentos.append({
            'id':dd[0],
            'producto':dd[1],
            'fecInicVig':dd[2],
            'fecTermVig':dd[3],
            'porcDescueto':dd[4]
        })


    producto = {
        'id':prod_datos[0],
        'nomProducto':prod_datos[1],
        'descProducto':prod_datos[2],
        'idSubCat':prod_datos[3],
        'nomSubCat':prod_datos[4],
        'idCat':prod_datos[5],
        'nomCat':prod_datos[6],
        'idMarca':prod_datos[7],
        'nomMarca':prod_datos[8],
        'opcion':prod_datos[9],
        'productoActivo':prod_datos[10],
        'retiroSucursal':prod_datos[11],
        'despachoDomicilio':prod_datos[12],
        'imagenes':imagenes,
        'precios':precios,
        'especificaciones':especificaciones,
        'stock':stock,
        'descuentos':descuentos
    }

    return producto, 200

def eliminar_imagen(con, id):
    cursor = con.connection.cursor()
    sql = "DELETE FROM imagenProducto WHERE id = %s"
    cursor.execute(sql, (id,))
    con.connection.commit()
    cursor.close()
    return jsonify({'mensaje':'borrado con exito'})

def editar_producto(con, data, imagenes, id):
    nombre = data['nomProducto']
    descripcion = data['descProducto']
    subcategoria = data['subCategoria']
    opcion = data['opcion']
    retiro = int(data['retiroSucursal'])
    despacho = int(data['despachoDomicilio'])
    activo = int(data['productoActivo'])

    cursor = con.connection.cursor()


    if data['marca']['nueva']:
        nombre = data['marca']['nombre']
        sql_marca = 'INSERT INTO marca (nomMarca) VALUES (%s)'
        cursor.execute(sql_marca, (nombre,))
        id_marca = cursor.lastrowid
    else:
        id_marca = int(data['marca']['id'])

    sql = """UPDATE productos SET   nomProducto = %s, 
                                    descProducto = %s, 
                                    subCatProducto = %s, 
                                    marcaProducto = %s, 
                                    opcion = %s, 
                                    productoActive = %s, 
                                    retiroSucursal = %s, 
                                    despachoDomicilio = %s
                                    WHERE id = %s"""
    
    cursor.execute(sql, (nombre, descripcion, subcategoria, id_marca, opcion, activo, retiro, despacho, id))

    sqlImagen = ('INSERT INTO imagenProducto (producto, imagen) VALUES (%s, %s)')

    for img in imagenes:
        if img.filename != '':
            result = cloudinary.uploader.upload(
                img,
                folder="productos",
                public_id=f"{id}_{uuid.uuid4().hex}"
            )

            public_id_completo = result['public_id'] 
            formato = result['format']                

            nombre_sin_folder = public_id_completo.split('/')[-1]  # 46_abc123xyz
            nombre_archivo = f"{nombre_sin_folder}.{formato}"  # 46_abc123xyz.webp
            cursor.execute(sqlImagen, (id, nombre_archivo))
    
    con.connection.commit()
    cursor.close()

    response = jsonify({'mensaje':'Producto modificado con exito'})
    response.status_code = 200
    return response
    
def eliminar_especificacion(con, id):
    cursor = con.connection.cursor()
    sql = "DELETE FROM especificacionProducto WHERE id = %s"
    cursor.execute(sql, (id,))
    con.connection.commit()
    cursor.close()

    return jsonify({'mensaje':'Especificación eliminada'})

def editar_especificacion(con, especs):
    cursor = con.connection.cursor()
    sql_update = "UPDATE especificacionProducto SET nombreEspecificacion = %s, valorEspecificacion = %s WHERE id = %s"
    sql_insert = "INSERT INTO especificacionProducto (producto, nombreEspecificacion, valorEspecificacion) VALUES (%s, %s, %s)"

    for espec in especs:
        if espec['id'] is None:
            cursor.execute(sql_insert, (espec['producto'], espec['nombre'], espec['valor']))
        else:
            cursor.execute(sql_update, (espec['nombre'], espec['valor'], espec['id']))   

    con.connection.commit()
    cursor.close()

    return jsonify({'mensaje':'Cambios realizados con exito'})

def editar_opciones(con, opciones):
    cursor = con.connection.cursor()
    print(opciones)
    sql_update_op = "UPDATE opcionProducto SET glosaOpcion = %s, opcionActiva = %s WHERE id = %s"
    sql_stock = "INSERT INTO inventario (producto, stock, sucursal) VALUES (%s,%s,%s)"
    sql_insert_op = "INSERT INTO opcionProducto (producto, glosaOpcion, opcionActiva) VALUES (%s,%s, 1)"


    try:
        con.connection.begin()
        for opcion in opciones:
            op = opcion['opcion']
            if op['id'] is not None:
                cursor.execute(sql_update_op, (op['nombre'], op['activa'], op['id']))
                id_opcion = op['id']
            else:
                cursor.execute(sql_insert_op, (opcion['producto'], op['nombre']))
                id_opcion = cursor.lastrowid

            if opcion['cantidad'] is not None:
                cursor.execute(sql_stock, (id_opcion, opcion['cantidad'], opcion['sucursal']))

        con.connection.commit()
        cursor.close()

        return jsonify({'mensaje':'Cambios realizado con exito'})
    except Exception as e:
        con.connection.rollback()
        return jsonify({'mensaje':'Error cargando los datos', 'error':str(e)}), 400

def agregar_precio(con, data):
    fecInicioVig = data['fecInicioVig']
    producto = data['producto']
    valor = data['valorProducto']

    cursor = con.connection.cursor()

    sql_fecha_duplicada = """
        SELECT COUNT(*) FROM valorProducto
        WHERE producto = %s AND fecInicVigValor = %s
    """
    cursor.execute(sql_fecha_duplicada, (producto, fecInicioVig))
    duplicados = cursor.fetchone()[0]

    if duplicados > 0:
        cursor.close()
        return jsonify({'mensaje': 'Ya existe un precio con esa fecha de inicio de vigencia'}), 400

    sql_fecha_posterior = """
        SELECT COUNT(*) FROM valorProducto
        WHERE producto = %s AND fecInicVigValor > %s
    """
    cursor.execute(sql_fecha_posterior, (producto, fecInicioVig))
    posteriores = cursor.fetchone()[0]

    if posteriores > 0:
        cursor.close()
        return jsonify({'mensaje': 'No se puede ingresar una fecha anterior a una ya existente'}), 400

    sql_insert = "INSERT INTO valorProducto (producto, valorProducto, fecInicVigValor) VALUES (%s,%s,%s) "
    cursor.execute(sql_insert, (producto, valor, fecInicioVig))
    con.connection.commit()
    cursor.close()

    return jsonify({'mensaje':'Producto agregado con exito'})

def eliminar_precio(con, id):
    cursor = con.connection.cursor()
    sql = "DELETE FROM valorProducto WHERE id = %s"
    cursor.execute(sql, (id,))
    con.connection.commit()
    cursor.close()

    return jsonify({'mensaje':'precio eliminado correctamente'})

def agregar_descuento(con, data):
    producto = data['producto']
    fec_inicio = data['fecInicVig']
    fec_termino = data['fecTermVig']
    porcentaje = data['porcDescuento']

    cursor = con.connection.cursor()

    if fec_termino < fec_inicio:
        return jsonify({'mensaje': 'La fecha de término no puede ser menor que la fecha de inicio'}), 400

    sql_duplicada = """
        SELECT COUNT(*) FROM descuentoProducto
        WHERE producto = %s AND fecInicVigDescuento = %s
    """
    cursor.execute(sql_duplicada, (producto, fec_inicio))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        return jsonify({'mensaje': 'Ya existe un descuento con esa fecha de inicio'}), 400

    sql_cruce = """
        SELECT COUNT(*) FROM descuentoProducto
        WHERE producto = %s AND (
            (fecInicVigDescuento <= %s AND fecTermVigDescuento >= %s) OR
            (fecInicVigDescuento <= %s AND fecTermVigDescuento >= %s) OR
            (%s <= fecInicVigDescuento AND %s >= fecTermVigDescuento)
        )
    """
    cursor.execute(sql_cruce, (producto, fec_inicio, fec_inicio, fec_termino, fec_termino, fec_inicio, fec_termino))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        return jsonify({'mensaje': 'Ya existe un descuento en un rango de fechas que se cruza con el ingresado'}), 400

    sql_insert = """
        INSERT INTO descuentoProducto (producto, fecInicVigDescuento, fecTermVigDescuento, porcDescuento)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql_insert, (producto, fec_inicio, fec_termino, porcentaje))
    con.connection.commit()
    cursor.close()

    return jsonify({'mensaje': 'Descuento agregado con éxito'})
