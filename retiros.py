from flask import jsonify

def lista_retiros(con, id, desde, hasta):
    cursor = con.connection.cursor()

    if id:
        print('Busqueda por ID')
        sql = "SELECT * FROM v_retiros WHERE id = %s"
        cursor.execute(sql, (id,))
    elif desde and hasta:        
        print('Busqueda por fecha')
        sql = "SELECT * FROM v_retiros where fechaRetiro between %s AND %s"
        cursor.execute(sql, (desde, hasta))
    else:
        print('Busqueda total')
        sql = "SELECT * FROM v_retiros"
        cursor.execute(sql)

    datos_retiro = cursor.fetchall()
    retiros = []

    for dr in datos_retiro:
        retiros.append({
            'id':dr[0],
            'venta':dr[1],
            'idEstadoRetiro':dr[2],
            'glosaEstadoRetiro':dr[3],
            'fecRetiro':dr[4],
            'rutCliente':dr[5],
            'nombreCliente':dr[6],
            'mailCliente':dr[7]
        })

    return retiros

def detalle_retiro(con, id):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM v_detalle_retiro WHERE id = %s"
    cursor.execute(sql, (id,))
    dato = cursor.fetchone()
    
    if not dato:
        return None

    retiro = {
        'id': dato[0],
        'venta': dato[1],
        'idEstadoRetiro': dato[2],
        'glosaEstadoRetiro': dato[3],
        'fechaRetiro': dato[4],
        'rutCliente': dato[5],
        'nomCliente': dato[6],
        'mailCliente': dato[7],
        'idSucursal': dato[8],
        'nomSucursal': dato[9],
        'comuna': dato[10],
        'provincia': dato[11],
        'region': dato[12]
    }

    return retiro

def actualizar_estado_retiro(con, id, data):
    estado = data['estadoRetiro']
    cursor = con.connection.cursor()
    sql = "UPDATE retiro SET estadoRetiro = %s WHERE id = %s"
    cursor.execute(sql, (estado, id))
    con.connection.commit()
    cursor.close()

    return jsonify({'mensaje':'Estado cambiado con exito'})