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

def lista_sucursales(con):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM v_sucursal"
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