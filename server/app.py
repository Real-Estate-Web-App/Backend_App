from flask import Flask, request, abort, jsonify, session
from flask_bcrypt import Bcrypt
from flask_session import Session
from models import db, User
from config import AppConfig
from models import Role
import json

app = Flask(__name__)
app.config.from_object(AppConfig)

bcrypt = Bcrypt(app)
server_session = Session(app)
db.init_app(app)

with app.app_context():
    # db.drop_all()
    db.create_all()

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

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"] 
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "There isn't an account with this email"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 401

    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role.name
    })

@app.route("/user", methods=["GET"])
def get_logged_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "You're not logged in"}), 401

    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    })

if __name__ == "__main__":
    app.run(debug=True)