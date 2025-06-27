from flask import jsonify

def obtener_tienda(con):
    cursor = con.connection.cursor()
    sql = "SELECT * FROM tienda where id = 1"
    cursor.execute(sql)
    datos = cursor.fetchone()
    tienda = {
        'id':datos[0],
        'nombre':datos[1],
        'facebook':datos[2],
        'instagram':datos[3],
        'x':datos[4],
        'dominio':datos[5]
    }

    return tienda

def editar_tienda(con, data):
    nombre = data['nombre']
    dominio = data['dominio']
    facebook = data['facebook']
    instagram = data['instagram']
    x = data['x']
    cursor = con.connection.cursor()
    sql = "UPDATE tienda SET nomTienda = %s, facebookTienda = %s, instagramTienda = %s, xTienda = %s, dominioTienda = %s where id = 1"
    cursor.execute(sql, (nombre, facebook, instagram, x, dominio))
    con.connection.commit()
    cursor.close()
    
    return jsonify({'mensaje':'Cambio realizado correctamente'})