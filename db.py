from flask_mysqldb import MySQL
from flask import Flask
from flask_cors import CORS
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app)

conexion = MySQL(app)  # Conexión a la base de datos

def get_db():
    return conexion
