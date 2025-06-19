from flask import jsonify

def ingresar_venta(con, data):
    productos = data['productos']
    cliente = data['cliente']
    pago = data['pago']
    nroTarjeta = pago['nroTarjeta']
    fecVenTarjeta = pago['fecVenTarjeta']
    cvv = pago['cvv']
    monto = pago['monto']
    despacho = data.get('despacho') or None
    retiro = data.get('retiro') or None
    sucursal = data['sucursal']
    
    try:
        con.connection.begin()
        cursor = con.connection.cursor()

        if cliente:
            clienteId = cliente
            sqlVenta = 'INSERT INTO venta (cliente, fecVenta, estadoVenta) VALUES (%s, now(), 2)'

        else:
            clienteInvitado = data['clienteInvitado']
            rutCliente = clienteInvitado['rutCliente']
            nomCliente = clienteInvitado['nomCliente']
            apeCliente = clienteInvitado['apeCliente']
            mailCliente = clienteInvitado['mailCliente']

            sqlCliente = 'INSERT INTO clienteInvitado (rutClienteInv, nomClienteInv, apeClienteInv, mailClienteInv) values (%s,%s,%s,%s)'
            cursor.execute(sqlCliente, (rutCliente, nomCliente, apeCliente, mailCliente))
            clienteId = cursor.lastrowid

            sqlVenta = 'INSERT INTO venta (clienteInvitado, fecVenta, estadoVenta) VALUES (%s, now(), 2)'

        cursor.execute(sqlVenta, (clienteId,))
        ventaId = cursor.lastrowid

        sqlPago = 'INSERT INTO pago (venta, nroTarjeta, fecVencTarjeta, cvv, montoPago, estadoPago) VALUES (%s, %s, %s, %s, %s, 2)'
        cursor.execute(sqlPago, (ventaId, nroTarjeta, fecVenTarjeta, cvv, monto))
        pagoId = cursor.lastrowid

        if despacho:
            calleDespacho = despacho['calleDespacho']
            numeroCalleDespacho = despacho['numeroCalleDespacho']
            comunaDespacho = despacho['comunaDespacho']
            sqlDespacho = 'INSERT INTO despacho (venta, estadodespacho, calleDespacho, numeroCalleDespacho, comunaDespacho) VALUES (%s, 1, %s, %s, %s)'

            cursor.execute(sqlDespacho, (ventaId, calleDespacho, numeroCalleDespacho, comunaDespacho))

        elif retiro:
            sqlRetiro = 'INSERT INTO retiro (venta, estadoRetiro, sucursalRetiro) VALUES (%s, 1, %s)'
            cursor.execute(sqlRetiro, (ventaId, sucursal))

        sqlStock = 'INSERT INTO inventario (producto, stock, sucursal) VALUES (%s, %s, %s)'
        sqlDetalle = 'INSERT INTO detalleVenta (venta, producto) VALUES (%s, %s)'

        for p in productos:
            producto = p['producto']
            opcion = p['opcion']
            cant = (int(p['cant']) * -1)
            
            cursor.execute(sqlDetalle, (ventaId, producto))
            cursor.execute(sqlStock, (opcion, cant, sucursal))

        con.connection.commit()
        response = jsonify({'mensaje':'Compra realizada con exito', 'venta':ventaId})
        response.status_code = 200
        return response

    except Exception as e:
        con.connection.rollback()
        response = jsonify({'mensaje':f"Error con la venta: {e}"})
        response.status_code = 400
        return response

def ver_ventas(con):
    try:
        cursor = con.connection.cursor()
        sql = "SELECT * FROM v_ventas"
        cursor.execute(sql)
        datos = cursor.fetchall()
        ventas = []
        for d in datos:
            venta = {'id':d[0],
                    'rut':d[1],
                    'nombre':d[2],
                    'mail':d[3],
                    'fecVenta':d[4].strftime("%d-%m-%Y %H:%M"),
                    'estadoVenta':d[5],
                    'glosaEstadoVenta':d[6]}
            ventas.append(venta)
        response = jsonify({'Mensaje':'Datos obtenidos correctamente', 'Ventas':ventas})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({'mensaje':'Error al recuperar datos', 'Error':str(e)})
        response.status_code = 500
        return response

def ver_pagos(con, venta):
    try:
        cursor = con.connection.cursor()
        sql = "SELECT * FROM v_pagos where venta = %s"
        cursor.execute(sql, (venta, ))
        datos = cursor.fetchall()

        pagos = []
        for d in datos:
            pago = {'id':d[0],
                    'venta':d[1],
                    'nroTarjeta':d[2],
                    'MontoPago':d[3],
                    'estadoPago':d[4],
                    'glosaEstadoPago':d[5]}
            pagos.append(pago)
        response = jsonify({'mensaje':'Datos conseguidos correctamente','Pagos':pagos})        
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({'mensaje':'Error al recuperar datos', 'Error':str(e)})
        response.status_code = 500
        return response
