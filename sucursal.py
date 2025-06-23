from flask import jsonify

def crear_sucursal(con, data):
    nom_sucursal = data['nomSucursal']
    direccion = data['direccion']
    comuna = data['comuna']
    tipo_sucursal = data['tipoSucursal']
    cursor = con.connection.cursor()
    sql = 'INSERT INTO sucursal (nomSucursal, direccionSucursal, comunaSucursal, tipoSucursal) VALUES (%s, %s, %s, %s)'
    cursor.execute(sql, (nom_sucursal, direccion, comuna, tipo_sucursal))
    con.connection.commit()
    response = jsonify({'mensaje':'Sucursal creada con exito'})
    response.status_code = 200
    return response

def lista_sucursales(con, todos):
    if todos == '1':
        sql = "SELECT * FROM v_sucursal"
    else:
        sql = "SELECT * FROM v_sucursal where activaSucursal = 1"
    cursor = con.connection.cursor()
    cursor.execute(sql)
    datos = cursor.fetchall()
    sucursales = []
    for i in datos:
        sucursal = {'id':i[0],
                    'nomSucursal':i[1],
                    'direccion':i[2],
                    'comuna':i[3],
                    'provincia':i[4],
                    'region':i[5],
                    'tipoSucursal':i[6],
                    'sucursalActiva':i[7]}
        sucursales.append(sucursal)
    response = jsonify({'mensaje':'Listado de Sucursales', 'sucursales':sucursales})
    response.status_code = 200
    return response    

def buscar_sucursal(con, id):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM v_sucursal_2 where id = %s"
    cursor.execute(sql, (id,))
    datos = cursor.fetchone()
    sucursal = {
        'id':datos[0],
        'nomSucursal':datos[1],
        'direccion':datos[2],
        'tipoSucursal':datos[3],
        'activaSucursal':datos[4],
        'comunaSucursal':datos[5],
        'provinciaSucursal':datos[6],
        'regionSucursal':datos[7]
    }

    return sucursal

def editar_sucursal(con, data, id):

    nomSucursal = data['nomSucursal']
    direccion = data['direccion']
    comuna = data['comuna']
    tipoSucursal = data['tipoSucursal']
    activaSucursal = data['activaSucursal']

    cursor = con.connection.cursor()
    sql = "UPDATE sucursal SET nomSucursal = %s, direccionSucursal = %s, comunaSucursal = %s, tipoSucursal = %s, activaSucursal = %s WHERE id = %s"
    cursor.execute(sql, (nomSucursal, direccion, comuna, tipoSucursal, activaSucursal, id))
    con.connection.commit()

    return jsonify({'mensaje':'Cambio realizado correctamente!!!'})

