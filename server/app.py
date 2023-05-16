from datetime import datetime
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from models import db, User, Buildings, Appointment
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

def get_suggestion(free_time, free_time_end, app_date, appointments):
    for appointment in appointments:
        appointment_date = appointment.app_date
        if appointment_date == app_date:
            appointment_time = appointment.app_time
            appointment_time_end = str(int(appointment_time[0:2]) + 1) + appointment_time[2:5]
            if len(appointment_time_end) != 5:
                appointment_time_end = "0" + appointment_time_end

            if appointment_time <= free_time and free_time_end <= appointment_time_end:
                return None
            else: 
                if appointment_time <= free_time and free_time < appointment_time_end and appointment_time_end <= free_time_end:
                    return None
                else:
                    if free_time <= appointment_time and appointment_time < free_time_end and free_time_end <= appointment_time_end:
                        return None
    return free_time

def get_suggestions_for_later(new_time, app_date, appointments):

    free_time_plus = str(int(new_time[0:2])) + new_time[2:5]
    if len(free_time_plus) != 5:
        free_time_plus = "0" + free_time_plus
        
    free_time_plus_end = str(int(free_time_plus[0:2]) + 1) + free_time_plus[2:5]
    if len(free_time_plus_end) != 5:
        free_time_plus_end = "0" + free_time_plus_end

    result_time = None
    while(free_time_plus < "24:00" and result_time is None):
        result_time = get_suggestion(free_time_plus, free_time_plus_end, app_date, appointments)
        free_time_plus = str(int(free_time_plus[0:2]) + 1) + free_time_plus[2:5]
        if len(free_time_plus) != 5:
            free_time_plus = "0" + free_time_plus

        free_time_plus_end = str(int(free_time_plus[0:2]) + 1) + free_time_plus[2:5]
        if len(free_time_plus_end) != 5:
            free_time_plus_end = "0" + free_time_plus_end
    
    return result_time

def get_suggestions_for_earlier(new_time, app_date, appointments):
    free_time_minus = str(int(new_time[0:2])) + new_time[2:5]
    if len(free_time_minus) != 5:
        free_time_minus = "0" + free_time_minus
        
    free_time_minus_end = str(int(free_time_minus[0:2]) + 1) + free_time_minus[2:5]
    if len(free_time_minus_end) != 5:
        free_time_minus_end = "0" + free_time_minus_end

    result_time = None
    while(free_time_minus > "00:00" and result_time is None):
        # print("Ealier time: " + free_time_minus)
        result_time = get_suggestion(free_time_minus, free_time_minus_end, app_date, appointments)
        free_time_minus = str(int(free_time_minus[0:2]) - 1) + free_time_minus[2:5]
        if len(free_time_minus) != 5:
            free_time_minus = "0" + free_time_minus

        free_time_minus_end = str(int(free_time_minus[0:2]) + 1) + free_time_minus[2:5]
        if len(free_time_minus_end) != 5:
            free_time_minus_end = "0" + free_time_minus_end
    return result_time

@cross_origin
@app.route("/makeAppointment", methods=["POST"])
def make_appointment():
    building_id = request.json["building_id"]
    user_id = request.json["user_id"]
    app_date = request.json["app_date"]
    app_time = request.json["app_time"]

    error = 0
    
    app_time_end = str(int(app_time[0:2]) + 1) + app_time[2:5]
    if len(app_time_end) != 5:
        app_time_end = "0" + app_time_end
    
    # print("received time: " + app_time)
    # print("received date:" + app_date)

    current_date_time = datetime.now()
    date = current_date_time.strftime("%Y-%m-%d")
    time = current_date_time.strftime("%H:%M")

    if (app_date < date or (app_date == date and app_time < time)):
        error = 1

    appointments = Appointment.query.filter_by(building_id=building_id)
    result_plus = None
    result_minus = None
    for appointment in appointments:
        appointment_date = appointment.app_date
        if appointment_date == app_date:
            
            appointment_time = appointment.app_time
            appointment_time_end = str(int(appointment_time[0:2]) + 1) + appointment_time[2:5]
            if len(appointment_time_end) != 5:
                appointment_time_end = "0" + appointment_time_end

            if appointment_time <= app_time and app_time_end <= appointment_time_end:
                error = 2
                error_time = appointment_time
                last_result_plus = get_suggestions_for_later(error_time, app_date, appointments)
                last_result_minus = get_suggestions_for_earlier(error_time, app_date, appointments)
                if result_plus is None:
                    result_plus = last_result_plus
                else:
                    if result_plus > last_result_plus:
                        result_plus = last_result_plus
                if result_minus is None:
                    result_minus = last_result_minus
                else:
                    if result_minus < last_result_minus:
                        result_minus = last_result_minus
            else: 
                if appointment_time <= app_time and app_time < appointment_time_end and appointment_time_end <= app_time_end:
                    error = 2
                    error_time = appointment_time
                    last_result_plus = get_suggestions_for_later(error_time, app_date, appointments)
                    last_result_minus = get_suggestions_for_earlier(error_time, app_date, appointments)
                    if result_plus is None:
                        result_plus = last_result_plus
                    else:
                        if result_plus > last_result_plus:
                            result_plus = last_result_plus
                    if result_minus is None:
                        result_minus = last_result_minus
                    else:
                        if result_minus < last_result_minus:
                            result_minus = last_result_minus
                else:
                    if app_time <= appointment_time and appointment_time < app_time_end and app_time_end <= appointment_time_end:
                        error = 2
                        error_time = appointment_time
                        last_result_plus = get_suggestions_for_later(error_time, app_date, appointments)
                        last_result_minus = get_suggestions_for_earlier(error_time, app_date, appointments)
                        if result_plus is None:
                            result_plus = last_result_plus
                        else:
                            if result_plus > last_result_plus:
                                result_plus = last_result_plus
                        if result_minus is None:
                            result_minus = last_result_minus
                        else:
                            if result_minus < last_result_minus:
                                result_minus = last_result_minus

    # print("Sugg for later: " + str(result_plus))
    # print("Sugg for ealier: " + str(result_minus))

    if error == 1:
        return jsonify({"error": "Date and time can't be in the past"}), 401
    if error == 2:
        if result_plus is None and result_minus is None:
            return jsonify({"error": "There is already an appointment at this date and hour. There's no empty spot today, try another day!"}), 401
        else:
            if result_plus is not None and result_minus is not None:
                if abs(int(app_time[0:2]) - int(result_plus[0:2])) > abs(int(app_time[0:2]) - int(result_minus[0:2])):
                    return jsonify({"error": "There is already an appointment at this date and hour. The next empty spot for the chosen day is: %s!" % (result_minus)}), 401
                else:
                    if abs(int(app_time[0:2]) - int(result_plus[0:2])) < abs(int(app_time[0:2]) - int(result_minus[0:2])):
                        return jsonify({"error": "There is already an appointment at this date and hour. The next empty spot for the chosen day is: %s!" % (result_plus)}), 401
                    else:
                        if abs(int(app_time[3:5]) - int(result_plus[3:5])) > abs(int(app_time[3:5]) - int(result_minus[3:5])):
                            return jsonify({"error": "There is already an appointment at this date and hour. The next empty spot for the chosen day is: %s!" % (result_minus)}), 401
                        else:
                            return jsonify({"error": "There is already an appointment at this date and hour. The next empty spot for the chosen day is: %s!" % (result_plus)}), 401
            else:
                if result_plus is None:
                    return jsonify({"error": "There is already an appointment at this date and hour. The next empty spot for the chosen day is: %s!" % (result_minus)}), 401
                else:
                    return jsonify({"error": "There is already an appointment at this date and hour. The next empty spot for the chosen day is: %s!" % (result_plus)}), 401

    new_appointment = Appointment(building_id=building_id, user_id=user_id, app_date=app_date, app_time=app_time)
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({
        "app_id": new_appointment.id,
    }), "200"

@cross_origin
@app.route("/getAppointments", methods=["GET"])
def get_all_appointments_for_month():
    args = request.args
    building_id = args.get("building_id")
    month = args.get("month")

    all_appointments = Appointment.query.filter_by(building_id=building_id)
    this_months_appointments = {}
    for appointment in all_appointments:
        app_month = appointment.app_date[5:7]
        if app_month == month:
            day = appointment.app_date[8:10]
            if day in this_months_appointments.keys():
                this_months_appointments[day] += 1
            else:
                this_months_appointments[day] = 1
    
    for key, value in this_months_appointments.items():
        print("Day " + key + ", has " + str(value) + " appointments")
    
    print("Building id: " + building_id)
    print("Month: " + month)

    return jsonify(this_months_appointments), "200"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    app.run(debug=True)