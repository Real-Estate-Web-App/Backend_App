from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from models import db, User, Buildings
from config import AppConfig
from models import Role

app = Flask(__name__)
app.config.from_object(AppConfig)

bcrypt = Bcrypt(app)
cors = CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)

with app.app_context():
    # db.drop_all()
    db.create_all()

# User requests:

@cross_origin
@app.route("/register", methods=["POST"])
def register_user():
    email = request.json["email"] 
    password = request.json["password"]
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "User already exists"}), 409

    hashed_pass = bcrypt.generate_password_hash(password)
    new_user = User(email=email, password=hashed_pass, first_name=first_name, last_name=last_name, role=Role.CLIENT)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })

@cross_origin
@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"] 
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "There isn't an account with this email"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 401

    # create a session for the logged user (tot timpul una noua -> o stergem la logout?):
    # session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role.name
    })

@cross_origin
@app.route("/user", methods=["POST"])
def get_logged_user():
    # user_id = session.get("user_id")

    user_id = request.json["id"]

    if not user_id:
        return jsonify({"error": "You're not logged in"}), 401

    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    })

@cross_origin
@app.route("/logout", methods=["GET"])
def logout_user():
    # user_id = session.get("user_id")

    # if user_id:
        # session.pop("user_id")
    return "200" # always return 200, but if user is logged in, delete its session

@cross_origin
@app.route("/updateProfile", methods=["POST"])
def update_user_profile():
    user_id = request.json["id"]
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    if not user_id:
        return jsonify({"error": "You're not logged in"}), 401

    user = User.query.filter_by(id=user_id).first()
    user.first_name = user_first_name
    user.last_name = user_last_name
    db.session.add(user)
    db.session.commit()

    return "200"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Buildings requests:
@cross_origin
@app.route("/createBuilding", methods=["POST"])
def create_building():
    type = request.json["type"]
    building_type = request.json["building_type"]
    image = request.json["image"]
    description = request.json["description"]
    address = request.json["address"]
    total_price = request.json["total_price"]
    nb_of_rooms = request.json["nb_of_rooms"]
    area = request.json["area"]

    new_building = Buildings(type=type, building_type=building_type, image=image, description=description, address=address, total_price=total_price, nb_of_rooms=nb_of_rooms, area=area)
    db.session.add(new_building)
    db.session.commit()

    return jsonify({
        "id": new_building.id,
        "type": new_building.type.name,
        "image": new_building.image,
        "description": new_building.description,
        "address": new_building.address,
        "total_price": new_building.total_price,
        "nb_of_rooms": new_building.nb_of_rooms,
        "area": new_building.area,
    })

@cross_origin
@app.route("/getBuildings", methods=["GET"])
def get_all_buildings():

    buildings = Buildings.query.all()
    proccessed_buildings = []

    for building in buildings:
        returned_building = {
            "id": building.id,
            "type": building.type.name,
            "building_type": building.building_type.name,
            "image": building.image,
            "description": building.description,
            "address": building.address,
            "total_price": building.total_price,
            "nb_of_rooms": building.nb_of_rooms,
            "area": building.area
        }
        proccessed_buildings.append(returned_building)

    return jsonify(
        proccessed_buildings
    )

@cross_origin
@app.route("/updateBuilding", methods=["POST"])
def update_building():
    id = request.json["id"]
    type = request.json["type"]
    image = request.json["image"]
    description = request.json["description"]
    total_price = request.json["total_price"]
    nb_of_rooms = request.json["nb_of_rooms"]
    area = request.json["area"]

    building = Buildings.query.filter_by(id=id).first()
    building.type = type
    building.image = image
    building.description = description
    building.total_price = total_price
    building.nb_of_rooms = nb_of_rooms
    building.area = area

    db.session.add(building)
    db.session.commit()

    return "200"

@cross_origin
@app.route("/deleteBuilding", methods=["POST"])
def delete_building():
    id = request.json["id"]

    Buildings.query.filter_by(id=id).delete()
    db.session.commit()

    return "200"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    app.run(debug=True)