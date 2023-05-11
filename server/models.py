from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from enum import Enum

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class Role(Enum):
    ADMIN=0
    CLIENT=1

class Type(Enum):
    RENT=0
    BUY=1

class BuildingType(Enum):
    STUDIO=0
    APARTMENT=1
    HOUSE=2

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(320), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)

class Buildings(db.Model):
    __tablename__ = "buildings"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    type = db.Column(db.Enum(Type), nullable=False)
    building_type = db.Column(db.Enum(BuildingType), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))
    address = db.Column(db.String(30), nullable=False)
    total_price = db.Column(db.String(10), nullable=False)
    nb_of_rooms = db.Column(db.String(10), nullable=False)
    area = db.Column(db.String(10), nullable=False)

class Appointment(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    building_id = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.String(32), nullable=False)
    app_date = db.Column(db.String(10), nullable=False)
    app_time = db.Column(db.String(5), nullable=False) 
