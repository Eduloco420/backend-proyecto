import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig():
    DEBUG= bool(os.getenv("DEBUG", "False") == "True")  
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    
config = {
    'development': DevelopmentConfig
}