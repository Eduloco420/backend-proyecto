from flask import Flask, jsonify
from flask_mysqldb import MySQL
from config import config
from dotenv import load_dotenv
from login import routes_auth
from db import app

app.register_blueprint(routes_auth)

@app.route('/ping')
def ping():
    return 'Pong!'

@app.route('/inicio', methods=['GET'])
def inicio():
    return 'Hola!!!'

@app.route('/prueba', methods=['GET'])
def prueba(): 
    cursor = conexion.connection.cursor()
    sql = 'SELECT * FROM comuna'
    cursor.execute(sql)
    datos = cursor.fetchall()
    comunas = []
    for fila in datos:
        comuna = {'id':fila[0],
                'nombreComuna':fila[1],
                'provincia':fila[2]}
        comunas.append(comuna)
    return jsonify({'comunas':comunas, 'mensaje':'Consula OK'})    

if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True)
