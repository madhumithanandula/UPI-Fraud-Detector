# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'Sample@112121'  # Replace this with a strong key
