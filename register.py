from flask import jsonify
from hashed import hash_password
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

def enviar_correo(destinatario, nombre, apellido, dominio):
    remitente = os.getenv('MAIL')
    password = os.getenv('MAIL_PASS')

    servidor_smtp = "smtp.gmail.com"
    puerto = 587  

    print(f'remitente: {remitente}')
    print(f'password: {password}')

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
        # Conectar con el servidor y enviar correo
        servidor = smtplib.SMTP(servidor_smtp, puerto)
        servidor.starttls()  # Iniciar conexión segura
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