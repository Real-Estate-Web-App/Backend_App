from flask import Flask, request, abort, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from models import db, User
from config import AppConfig
from models import Role
import json

app = Flask(__name__)
app.config.from_object(AppConfig)

bcrypt = Bcrypt(app)
cors = CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)

with app.app_context():
    # db.drop_all()
    db.create_all()

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

if __name__ == "__main__":
    app.run(debug=True)