from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))  # ссылка на обложку
    category = db.Column(db.String(100))
    year = db.Column(db.Integer)
    torrent_data = db.Column(db.LargeBinary)  # сам .torrent файл
    torrent_filename = db.Column(db.String(200))  # имя файла для скачивания
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
