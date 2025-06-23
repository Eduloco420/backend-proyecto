from flask import jsonify

def obtener_region(con):
    cursor = con.connection.cursor()
    sql = "select id, nomRegion from region"
    cursor.execute(sql)
    datos = cursor.fetchall()
    regiones = []
    for d in datos:
        regiones.append({
            'id':d[0],
            'nombre':d[1]
        })
    
    return regiones

def obtener_provincia(con, region):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM provincia where region = %s"
    cursor.execute(sql, (region,))
    datos = cursor.fetchall()
    provincias = []
    for d in datos:
        provincias.append({
            'id':d[0],
            'nombre':d[1],
            'region':d[2]
        })
    return provincias        

def obtener_comuna(con, provincia):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM comuna WHERE provincia = %s"
    cursor.execute(sql, (provincia,))
    datos = cursor.fetchall()
    comunas = []
    for d in datos:
        comunas.append({
            'id':d[0],
            'nombre':d[1],
            'provincia':d[2]
        })
    return comunas        

def obtener_ubicaciones(con):
    cursor = con.connection.cursor()
    sql_region = "SELECT id, nomRegion FROM region"
    sql_provincia = "SELECT * FROM provincia"
    sql_comuna = "SELECT * FROM comuna"

    regiones = []
    provincias = []
    comunas = []
    
    cursor.execute(sql_region)
    datos_region = cursor.fetchall()

    cursor.execute(sql_provincia)
    datos_provincia = cursor.fetchall()

    cursor.execute(sql_comuna)
    datos_comuna = cursor.fetchall()

    for d in datos_region:
        regiones.append({
            'id':d[0],
            'nombre':d[1]
        })

    for d in datos_provincia:
        provincias.append({
            'id':d[0],
            'nombre':d[1],
            'region':d[2]
        })
        
    for d in datos_comuna:
        comunas.append({
            'id':d[0],
            'nombre':d[1],
            'provincia':d[2]
        })

    response = jsonify({
        'regiones':regiones,
        'provincias':provincias,
        'comunas':comunas
    })     

    return response   