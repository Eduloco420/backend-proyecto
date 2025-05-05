from flask import jsonify
from hashed import hash_password
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import MySQLdb

def enviar_correo(destinatario, nombre, apellido, dominio):
    remitente = os.getenv('MAIL')
    password = os.getenv('MAIL_PASS')

    servidor_smtp = "smtp.gmail.com"
    puerto = 587  

    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = "Confirmación de Registro"

    cuerpo = f"""
    Hola {nombre} {apellido},

    Gracias por registrarte en nuestro sitio. 
    Activa tu cuenta haciendo clic en el siguiente enlace:

    {dominio}/activar-cuenta?email={destinatario}

    Saludos,
    Tu equipo.
    """
    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        servidor = smtplib.SMTP(servidor_smtp, puerto)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print("Correo enviado con éxito")
    except Exception as e:
        print(f"Error enviando correo: {str(e)}")

def registrar(con, data):
    rut = data['rut']
    nombre = data['nombre']
    apellido = data['apellido']
    mail = data['mail']
    rol = data['rol']
    password = data['password']

    try:

        hashedPassword = hash_password(password)

        con.connection.begin()
        cursor = con.connection.cursor()
        sql = ('INSERT INTO usuario (rutUsuario, nomUsuario, apeUsuario, mailUsuario, rolUsuario, passUsuario, fecCreacionUsuario, activeUsuario) VALUES (%s, %s, %s, %s, %s, %s, now(), false);')
        cursor.execute(sql, (rut,nombre,apellido,mail,rol,hashedPassword))

        con.connection.commit()
        sql = 'SELECT dominioTienda from tienda'
        cursor.execute(sql)
        dominio = cursor.fetchone()[0]
        enviar_correo(destinatario=mail, nombre=nombre, apellido=apellido, dominio=dominio)
        response = jsonify({'mensaje':'Usuario creado con exito'})
        response.status_code = 200
        return response
    
    except MySQLdb.IntegrityError as e:
        if e.args[0] == 1062:
            error_msg = str(e.args[1])
            if 'rutUsuario' in error_msg:
                return jsonify({'mensaje': 'El RUT ya está registrado'}), 400
            elif 'mailUsuario' in error_msg:
                return jsonify({'mensaje': 'El correo ya está registrado'}), 400
            else:
                return jsonify({'mensaje': 'Dato duplicado'}), 400
        else:
            return jsonify({'mensaje': 'Error de integridad', 'detalle': str(e)}), 400
    
    except Exception as e:
        con.connection.rollback()
        return jsonify({'mensaje':'Error en la creación de usuario ' + str(e)})
    
def validar_cuenta(con, data):
    cursor = con.connection.cursor()
    usuario_id = data['id']
    sql = 'UPDATE usuario SET activeUsuario = 1 WHERE id = %s'
    cursor.execute(sql, (usuario_id, ))
    response = jsonify({'mensaje':'Usuario activado con exito'})
    response.status_code = 200
    return response

def recuperar_contraseña(con, data):
    
    email = data['email']
    
    cursor = con.connection.cursor()
    sql = 'SELECT nomUsuario, apeUsuario, mailUsuario, id FROM usuario WHERE lower(mailUsuario) = %s AND activeUsuario = 1;'
    cursor.execute(sql, (email,))
    
    datos = cursor.fetchone()

    if datos:

        sql = 'SELECT dominioTienda from tienda'
        cursor.execute(sql)

        dominio = cursor.fetchone()[0]
        
        nombre = datos[0]
        apellido = datos[1]
        mail = datos[2]
        idUsuario = datos[3]

        remitente = os.getenv('MAIL')
        password = os.getenv('MAIL_PASS')

        servidor_smtp = "smtp.gmail.com"
        puerto = 587

        msg = MIMEMultipart()
        msg["From"] = remitente
        msg["To"] = mail
        msg["Subject"] = "Confirmación de Registro"

        cuerpo = f"""
        Hola {nombre} {apellido},

        Para recuperar tu contraseña, haz click en el siguiente enlace:

        {dominio}/activar-cuenta?email={idUsuario}

        Saludos,
        Tu equipo.
        """

        msg.attach(MIMEText(cuerpo, "plain"))

        try:
            servidor = smtplib.SMTP(servidor_smtp, puerto)
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.sendmail(remitente, email, msg.as_string())
            servidor.quit()
            response = jsonify({'mensaje':'Se han enviado las instrucciones para restablecer la contraseña al correo electronico ingresado'})
            response.status_code = 200
            return response
        except Exception as e:
            response = jsonify({'mensaje':'Error al momento de enviar correo electronico', 'error':e})
            response.status_code = 500
            return response
        
    else:
        response = jsonify({'mensaje':'El correo electronico ingresado no se encuentra registrado en el sistema'})
        response.status_code = 404
        return response

def cambiar_contraseña(con, data):
    usuario = data['usuario']
    password = data['password']
    hashedPassword = hash_password(password)

    try:
        con.connection.begin()
        cursor = con.connection.cursor()
        sql = 'UPDATE usuario SET passUsuario = %s WHERE id = %s'
        cursor.execute(sql, (hashedPassword, usuario))

        if cursor.rowcount == 0:
            con.connection.rollback()
            response = jsonify({'mensaje': 'El ID de usuario no existe'})
            response.status_code = 404
            return response

        con.connection.commit()

        response = jsonify({'mensaje':'Contraseña cambiada con exito'})
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({'mensaje':'Error cambiando la contraseña','error':e})
        response.status_code = 400
        return response

def ver_usuario(con, rut, mail):
    cursor = con.connection.cursor()

    if not rut and not mail:
        response = jsonify({'mensaje':'Se debe especificar un Rut o Correo Electrónico'})
        response.status_code = 404
        return response

    if rut:
        sql = "SELECT id, rutUsuario, nomUsuario, apeUsuario, mailUsuario, rolUsuario, activeUsuario FROM usuario WHERE lower(rutUsuario) = %s"
        cursor.execute(sql, (rut,))
    if mail:
        sql = "SELECT id, rutUsuario, nomUsuario, apeUsuario, mailUsuario, rolUsuario, activeUsuario FROM usuario WHERE lower(mailUsuario) = %s"
        cursor.execute(sql, (mail,))

    datos = cursor.fetchone()

    if datos:
        usuario = {'id':datos[0],
                'rut':datos[1],
                'nombre':datos[2],
                'apellido':datos[3],
                'mail':datos[4],
                'rol':datos[5],
                'activo':datos[6]}
        
        response = jsonify({'mensaje':'Datos conseguidos', 'usuario':usuario})
        response.status_code = 200
        return response
    else:
        response = jsonify({'mensaje':'No se han encontrado datos'})
        response.status_code = 404
        return response
    
def actualizar_user(con, data, id):
    rut = data['rut']
    mail = data['mail']
    nombre = data['nombre']
    apellido = data['apellido']
    rol = data['rol']
    vigente = data['vigente']
    password = data.get('password')  

    con.connection.begin()
    cursor = con.connection.cursor()

    if password:
        hashedPassword = hash_password(password)
        sql = "UPDATE usuario SET rutUsuario = %s, mailUsuario = %s, nomUsuario = %s, apeUsuario = %s, rolUsuario = %s, passUsuario = %s, activeUsuario = %s WHERE id = %s"
        cursor.execute(sql, (rut, mail, nombre, apellido, rol, hashedPassword, vigente, id))
    else:
        sql = "UPDATE usuario SET rutUsuario = %s, mailUsuario = %s, nomUsuario = %s, apeUsuario = %s, rolUsuario = %s, activeUsuario = %s WHERE id = %s"
        cursor.execute(sql, (rut, mail, nombre, apellido, rol, vigente, id))

    con.connection.commit()

    if cursor.rowcount == 0:
        response = jsonify({'mensaje':'No se realizo ningun cambio'})
        response.status_code = 400
        return response
    
    response = jsonify({'mensaje':'Se han actualizado los datos'})
    response.status_code = 200
    return response