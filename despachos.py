from flask import jsonify

def lista_despachos(con, id, desde, hasta):
    cursor = con.connection.cursor()

    if id:
        print('Busqueda por ID')
        sql = "SELECT * FROM v_despachos WHERE id = %s"
        cursor.execute(sql, (id,))
    elif desde and hasta:        
        print('Busqueda por fecha')
        sql = "SELECT * FROM v_despachos where fecDespacho between %s AND %s"
        cursor.execute(sql, (desde, hasta))
    else:
        print('Busqueda total')
        sql = "SELECT * FROM v_despachos"
        cursor.execute(sql)

    datos_despachos = cursor.fetchall()
    despachos = []

    for dd in datos_despachos:
        despachos.append({
            'id':dd[0],
            'venta':dd[1],
            'idEstadoDespacho':dd[2],
            'glosaEstadoDespacho':dd[3],
            'fecDespacho':dd[4],
            'rutCliente':dd[5],
            'nombreCliente':dd[6],
            'mailCliente':dd[7]
        })

    return despachos

def detalle_despacho(con, id):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM v_detalle_despacho WHERE id = %s"
    cursor.execute(sql, (id,))
    dato = cursor.fetchone()
    despacho = {
        'id':dato[0],
        'venta':dato[1],
        'idEstadoDespacho':dato[2],
        'glosaEstadoDespacho':dato[3],
        'fecDespacho':dato[4],
        'rutCliente':dato[5],
        'nomCliente':dato[6],
        'mailCliente':dato[7],
        'codSeguimiento':dato[8],
        'empresaDespacho':dato[9],
        'enlaceSeguimiento':dato[10],
        'fecEstimadaRecepcion':dato[11],
        'calleDespacho':dato[12],
        'numeroCalleDespacho':dato[13],
        'idComuna':dato[14],
        'comuna':dato[15],
        'idProvincia':dato[16],
        'provincia':dato[17],
        'idRegion':dato[18],
        'region':dato[19]
    }

    return despacho

def modificar_despacho(con, data, id):
    cod_seguimiento = data['codSeguimiento']
    empresa_despacho = data['empresaDespacho']
    enlace_seguimient = data['enlaceSeguimiento']
    fecha_recepcion = data['fecEstimadaRecepcion']
    estado = data['idEstadoDespacho']

    cursor = con.connection.cursor()

    sql = """UPDATE despacho SET 
                estadoDespacho = %s, 
                codSeguimiento = %s, 
                empresaDespacho = %s, 
                enlaceSeguimiento = %s, 
                fecEstimadaRecepcion = %s 
                WHERE id = %s"""
    cursor.execute(sql, (estado, cod_seguimiento, empresa_despacho, enlace_seguimient, fecha_recepcion, id))
    
    con.connection.commit()
    cursor.close()
    return jsonify({'mensaje':'Se han grabado los datos'})