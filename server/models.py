from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from enum import Enum

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class Role(Enum):
    ADMIN=0
    CLIENT=1

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(320), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)