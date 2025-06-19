from flask_mysqldb import MySQL
from flask import Flask
from flask_cors import CORS
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app, origins=[
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
])

conexion = MySQL(app)  # Conexión a la base de datos

def get_db():
    return conexion
