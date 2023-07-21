from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import base64
import pyotp
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

load_dotenv()
# Init app
app = Flask(__name__)
# Secret Key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Database
if os.getenv('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('PROD_DB_URI')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('NONPROD_DB_URI')
# Init DB
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)
# Init jwt
jwt = JWTManager(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pawscheck@gmail.com'
app.config['MAIL_PASSWORD'] = 'xmewgvshnwakaprc'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Model and Schema
class Owner(db.Model):
    __tablename__ = 'owner'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(200), unique=True, nullable=False)
    contact_number = db.Column(db.String(100), nullable=False)
    password = db.Column(db.Text, nullable=False)
    address = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    profile = db.Column(db.String)
    signature = db.Column(db.String, nullable=False)
    appointments = db.relationship('Appointment', backref='owner', lazy=True)
    pets = db.relationship('Pet', backref='owner', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class OwnerSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email_address", "contact_number", "password", "address", "age", "gender", "profile")

owner_schema = OwnerSchema()
owners_schema = OwnerSchema(many=True)

class Pet(db.Model):
    __tablename__ = 'pet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.String(100), nullable=False)
    markings = db.Column(db.String(100), nullable=False)
    vaccination = db.Column(db.String(100))
    deworming = db.Column(db.String(100))
    profile = db.Column(db.String, nullable=False)
    records = db.relationship('Record', backref='pet', lazy=True)
    appointments = db.relationship('Appointment', backref='pet', lazy=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)

class PetSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "age", "gender", "breed", "birthdate", "markings", "vaccination", "deworming", "profile")

pet_schema = PetSchema()
pets_schema = PetSchema(many=True)

""" class PetOwnerSchema(ma.Schema):
    class Meta:
        fields = ("pet_name", "pet_age", "pet_gender", "pet_breed", "pet_birthdate", "pet_markings", "pet_vaccination", "pet_deworming", "pet_profile", "owner_first_name", "owner_last_name", "owner_contact_number", "owner_address")

pet_owner_schema = PetOwnerSchema()
pets_owners_schema = PetOwnerSchema(many=True) """

class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    remedy = db.Column(db.String, nullable=False)
    comments = db.Column(db.String)
    create_date = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.String(100), nullable=False)
    clinical_sign_photo_1 = db.Column(db.String)
    clinical_sign_photo_2 = db.Column(db.String)
    clinical_sign_photo_3 = db.Column(db.String)
    clinical_sign_photo_4 = db.Column(db.String)
    clinical_sign_photo_5 = db.Column(db.String)
    records = db.relationship('Appointment', backref='record', lazy=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)

class RecordSchema(ma.Schema):
    class Meta:
        fields = ("id", "remedy", "comments", "create_date", "create_time", "clinical_sign_photo_1", "clinical_sign_photo_2",
                    "clinical_sign_photo_3", "clinical_sign_photo_4", "clinical_sign_photo_5")

record_schema = RecordSchema()
records_schema = RecordSchema(many=True)

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('record.id'))

class AppointmentSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "date", "time", "status")

appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)

class Vet(db.Model):
    __tablename__ = 'vet'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Routes

#Sign-up
@app.route('/signup', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email_address = request.form['email_address']
    contact_number = request.form['contact_number']
    password = request.form['password']
    address = request.form['address']
    age = request.form['age']
    gender = request.form['gender']
    
    signature_file = request.files['signature']
    signature = signature_file.read()

    signature_base64 = base64.b64encode(signature)

    if not first_name or not last_name or not email_address or not contact_number or not password or not address or not age or not gender:
        response = {
            "error": "Please input field"
        }

        return jsonify(response), 400

    existing_email = Owner.query.filter_by(email_address=email_address).first()

    if existing_email:
        response = {
            "error": "Email already exists"
        }

        return jsonify(response), 400

    owner = Owner(first_name = first_name, last_name = last_name, email_address = email_address,
                    contact_number = contact_number, address = address, age = age, gender = gender, signature = signature_base64)
    owner.set_password(password)

    db.session.add(owner)
    db.session.commit()

    access_token = create_access_token(identity = owner.id)
    response = {
        "message": "You registered successfully.",
        "access_token": access_token
    }

    return jsonify(response), 201

#Login
@app.route('/login', methods=['POST'])
def login_owner():
    email_address = request.form['email_address']
    password = request.form['password']

    owner = Owner.query.filter_by(email_address = email_address).first()
    vet = Vet.query.filter_by(email_address = email_address).first()
    admin = Admin.query.filter_by(email_address = email_address).first()

    if owner and owner.check_password(password):
        access_token = create_access_token(identity = owner.id)
        response = {
            "message": f"Welcome {owner.first_name} {owner.last_name}.",
            "access_token": access_token,
            "user_type": "owner"
        }

        return jsonify(response), 200
        
    elif vet and vet.check_password(password):
        access_token = create_access_token(identity = vet.id)
        response = {
            "message": f"Welcome {vet.first_name} {vet.last_name}.",
            "access_token": access_token,
            "user_type": "vet"
        }

        return jsonify(response), 200
  
    elif admin and admin.check_password(password):
        access_token = create_access_token(identity = admin.id)
        response = {
            "message": f"Welcome {admin.first_name} {admin.last_name}.",
            "access_token": access_token,
            "user_type": "admin"
        }

    response = {
        "error": "Invalid email or password"
    }

    return jsonify(response), 401

#Verification for changing password
@app.route('/verify', methods=['GET', 'PUT'])
def forgot_password_owner():
    email_address = request.form['email_address']
    input_totp = request.form['input_totp']

    # generating TOTP codes with provided secret
    totp = pyotp.TOTP("base32secret3232", interval = 60)
    secret = totp.now()

    owner = Owner.query.filter_by(email_address = email_address).first()
    if request.method == 'GET':
        if not owner:
            response = {
                "error": "Email does not exist"
            }

            return jsonify(response), 401

        msg = Message(subject = 'PawsCheck Verification Code', sender = 'pawscheck@gmail.com', recipients = [email_address])
        msg.body = f"{secret} is your verification code. \nPlease complete the account verification process in 60 seconds."
        mail.send(msg)
        
        response = {
            "message": f"Verification code is send to your email, {owner.email_address}",
            "code": f"{secret}"
        }

        return jsonify(response), 200

    if totp.verify(input_totp):
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            response = {
                "error": "Password does not match"
            }

            return jsonify(response), 401

        owner.password = request.form['new_password']
        owner.set_password(owner.password)

        db.session.commit()
        response = {
            "message": "Successfully Update"
        }

        return jsonify(response), 200

    response = {
        "message": "Invalid Verification Code"
    }

    return jsonify(response), 401

#GET owner
@app.route('/owner', methods=['GET'])
@jwt_required()
def get_owner():
    try: 
        owner_id = get_jwt_identity()

        owner = Owner.query.filter_by(id = owner_id).first()
        if owner:
            response = owner_schema.dump(owner)

            return jsonify(response), 200

    except (KeyError, TypeError):
        response = {
            "error": "Authentication expired"
        }
        
        return jsonify(response), 400

# ===============PET=======================================================================================================================

#GET list of pets based on owner
@app.route('/pets', methods=['GET'])
@jwt_required()
def all_pet():
    owner_id = get_jwt_identity()

    pets = Pet.query.filter_by(owner_id = owner_id).all()

    response = pets_schema.dump(pets)
    return jsonify(response), 200

#GET pet based on ID
@app.route('/pet/<int:pet_id>', methods=['GET'])
@jwt_required()
def get_pet(pet_id):
    owner_id = get_jwt_identity()
    join = db.session.query(Pet, Owner).join(Owner, Pet.owner_id == Owner.id).filter(owner_id == owner_id, Pet.id == pet_id).first()
    if join:
        pet, owner = join

        if owner.profile != None:
            pet_profile_base64 = pet.profile.decode()
            owner_profile_base64 = owner.profile.decode()

            results = {
                    'pet_name': pet.name,
                    'pet_age': pet.age,
                    'pet_gender': pet.gender,
                    'pet_breed': pet.breed,
                    'pet_birthdate': pet.birthdate,
                    'pet_markings': pet.markings,
                    'pet_vaccination': pet.vaccination,
                    'pet_deworming': pet.deworming,
                    'pet_profile': pet_profile_base64,

                    'owner_first_name': owner.first_name,
                    'owner_last_name': owner.last_name,
                    'owner_email_address': owner.email_address,
                    'owner_contact_number': owner.contact_number,
                    'owner_password': owner.password,
                    'owner_address': owner.address,
                    'owner_age': owner.age,
                    'owner_gender': owner.gender,
                    'owner_profile': owner_profile_base64
            }

            return jsonify(results), 200
        
        pet_profile_base64 = pet.profile.decode()

        results = {
                'pet_name': pet.name,
                'pet_age': pet.age,
                'pet_gender': pet.gender,
                'pet_breed': pet.breed,
                'pet_birthdate': pet.birthdate,
                'pet_markings': pet.markings,
                'pet_vaccination': pet.vaccination,
                'pet_deworming': pet.deworming,
                'pet_profile': pet_profile_base64,

                'owner_first_name': owner.first_name,
                'owner_last_name': owner.last_name,
                'owner_email_address': owner.email_address,
                'owner_contact_number': owner.contact_number,
                'owner_password': owner.password,
                'owner_address': owner.address,
                'owner_age': owner.age,
                'owner_gender': owner.gender
            }

        return jsonify(results), 200
    
    else:
        return jsonify({'message': 'Not found'}), 404

#PUT/EDIT pet information
@app.route('/pet/<int:pet_id>/update', methods=['PUT'])
@jwt_required()
def update_pet_owner(pet_id):
    try:
        owner_id = get_jwt_identity()
        join = db.session.query(Pet, Owner).join(Owner, Pet.owner_id == Owner.id).filter(owner_id == owner_id, Pet.id == pet_id).first()
        if join:
            pet, owner = join

            pet.name = request.form['name']
            pet.age = request.form['age']
            pet.gender = request.form['gender']
            pet.breed = request.form['breed']
            pet.birthdate = request.form['birthdate']
            pet.markings = request.form['markings']
            pet.vaccination = request.form['vaccination']
            pet.deworming = request.form['deworming']

            owner.first_name = request.form['first_name']
            owner.last_name = request.form['last_name']
            owner.contact_number = request.form['contact_number']
            owner.address = request.form['address'] 
            profile_file = request.files['profile']
            profile_read = profile_file.read()
            owner.profile = base64.b64encode(profile_read)
            
            db.session.commit()
            response = {
                "message": "Successfully Update"
            }

            return jsonify(response), 200

    except (ValueError, TypeError):
        response = {
            "error" : "Invalid data"
        }

        return jsonify(response), 400

#POST/ADD pet
@app.route('/pet', methods=['POST'])
@jwt_required()
def add_pet():
    try:
        owner_id = get_jwt_identity()

        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        breed = request.form['breed']
        birthdate = request.form['birthdate']
        markings = request.form['markings']
        vaccination = request.form['vaccination']
        deworming = request.form['deworming']
        profile_file = request.files['profile']
        profile = profile_file.read()
        profile_base64 = base64.b64encode(profile)

        pet = Pet(owner_id = owner_id, name = name, age = age, gender = gender,
                    breed = breed, birthdate = birthdate, markings = markings, vaccination = vaccination, deworming = deworming, profile = profile_base64)        

        db.session.add(pet)
        db.session.commit()

        response = {
            "message": f"You added your pet, {pet.name}"
        }

        return jsonify(response), 201

    except (KeyError, TypeError):
        response = {
            "error": "Invalid Data"
        }
        
        return jsonify(response), 400

#PUT/EDIT photo of pet
@app.route('/pet/<int:pet_id>/update/profile', methods=['PUT'])
@jwt_required()
def update_pet_photo(pet_id):
    try:
        owner_id = get_jwt_identity()

        pet = Pet.query.filter_by(id=pet_id, owner_id=owner_id).first()
        if pet:
            profile_file = request.files['profile']
            pet.profile = profile_file.read()
            
            db.session.commit()
            response = {
                "message": "Successfully Update"
            }

            return jsonify(response), 200

    except (ValueError, TypeError):
        response = {
            "error" : "Invalid data"
        }

        return jsonify(response), 400

#DELETE pet based on ID
@app.route('/pet/<int:pet_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    try:
        owner_id = get_jwt_identity()

        pet = Pet.query.filter_by(id=pet_id, owner_id=owner_id).first()
        if pet:
            db.session.delete(pet)            
            db.session.commit()
            response = {
                "message": "Successfully Delete"
            }

            return jsonify(response), 200

        else:
            response = {
                "message": "Pet Not Found"
            }

            return jsonify(response), 404

    except (ValueError, TypeError):
        response = {
            "error" : "Invalid data"
        }

        return jsonify(response), 400

# ==========RECORDS==========================================================================================================================

""" @app.route('/pet/<int:pet_id>/records', methods=['GET'])
@jwt_required()
def all_record(pet_id):
    records = Record.query.filter_by(pet_id = pet_id).all()

    response = records_schema.dump(records)
    return jsonify(response), 200 """

#POST/ADD record of pet based on pet ID
@app.route('/pet/<int:pet_id>/record', methods=['POST'])
@jwt_required()
def add_record(pet_id):
    try:
        remedy = request.form['remedy']
        comments = request.form['comments']
        create_date = request.form['create_date']
        create_time = request.form['create_time']

        clinical_sign_photo_1_file = request.files['clinical_sign_photo_1']
        clinical_sign_photo_1_read = clinical_sign_photo_1_file.read()
        clinical_sign_photo_1 = base64.b64encode(clinical_sign_photo_1_read)

        clinical_sign_photo_2_file = request.files['clinical_sign_photo_2']
        clinical_sign_photo_2_read = clinical_sign_photo_2_file.read()
        clinical_sign_photo_2 = base64.b64encode(clinical_sign_photo_2_read)

        clinical_sign_photo_3_file = request.files['clinical_sign_photo_3']
        clinical_sign_photo_3_read = clinical_sign_photo_3_file.read()
        clinical_sign_photo_3 = base64.b64encode(clinical_sign_photo_3_read)

        clinical_sign_photo_4_file = request.files['clinical_sign_photo_4']
        clinical_sign_photo_4_read = clinical_sign_photo_4_file.read()
        clinical_sign_photo_4 = base64.b64encode(clinical_sign_photo_4_read)

        clinical_sign_photo_5_file = request.files['clinical_sign_photo_5']
        clinical_sign_photo_5_read = clinical_sign_photo_5_file.read()
        clinical_sign_photo_5 = base64.b64encode(clinical_sign_photo_5_read)

        record = Record(pet_id = pet_id, remedy = remedy, comments = comments, create_date = create_date, create_time = create_time,
                        clinical_sign_photo_1 = clinical_sign_photo_1, clinical_sign_photo_2 = clinical_sign_photo_2,
                        clinical_sign_photo_3 = clinical_sign_photo_3, clinical_sign_photo_4 = clinical_sign_photo_4,
                        clinical_sign_photo_5 = clinical_sign_photo_5)

        db.session.add(record)
        db.session.commit()

        response = {
            "message": "The record is added"
        }

        return jsonify(response), 201

    except (KeyError, TypeError):
        response = {
            "error": "Invalid Data"
        }
        
        return jsonify(response), 400

 #GET record of pet   
@app.route('/pet/<int:pet_id>/records', methods=['GET'])
@jwt_required()
def list_records_pet(pet_id):

    join = db.session.query(Appointment, Record).outerjoin(Record, Appointment.record_id == Record.id, full=True).filter(or_(Appointment.pet_id == pet_id, Record.pet_id == pet_id)).all()

    """ if all(result[0] is None for result in join):
        if record.clinical_sign_photo_1 == None:
            result = [{
            'record_remedy': record.remedy if record else None,
            } for appointment, record in join]
            
            return jsonify(result), 200

        result = [{
            'record_remedy': record.remedy if record else None,
            'record_clinical_photo': record.clinical_sign_photo_1.decode() if record else None
            } for appointment, record in join]
            
        return jsonify(result), 200

    elif all(result[1] is None for result in join):
        result = [{
            'appointment_date': appointment.date if appointment else None,
            'appointment_time': appointment.time if appointment else None,
            'appointment_status': appointment.status if appointment else None
        } for appointment, record in join]
        
        return jsonify(result), 200 """

    if join:
        result = [{
            'appointment_date': appointment.date if appointment else None,
            'appointment_time': appointment.time if appointment else None,
            'appointment_status': appointment.status if appointment else None,
            'record_remedy': record.remedy if record else None,
            'record_clinical_photo': record.clinical_sign_photo_1.decode() if record else None
        } for appointment, record in join]
        
        return jsonify(result), 200
    
    elif not join:
        result = [{}]

        return result, 200


# ===========APPOINTMENTS======================================================================================================================

#GET list of appointments based on owner
@app.route('/appointment', methods=['GET'])
@jwt_required()
def all_appointment_owner():
    owner_id = get_jwt_identity()

    join = db.session.query(Appointment, Pet).join(Pet, Appointment.pet_id == Pet.id).filter(Pet.owner_id == owner_id).all()
    if join:

        results = [{
            'appointment_id': appointment.id,
            'appointment_title': appointment.title,
            'appointment_date': appointment.date,
            'appointment_time': appointment.time,
            'appointment_status': appointment.status,
            'pet_name': pet.name
        } for appointment, pet in join]

        return jsonify(results), 200

    return jsonify([]), 200

#GET appointment based on pet
@app.route('/pet/<int:pet_id>/appointment', methods=['GET'])
@jwt_required()
def all_appointment_pet(pet_id):

    appointments = Appointment.query.filter_by(pet_id = pet_id).all()

    response = appointments_schema.dump(appointments)
    return jsonify(response), 200

#GET appointments based on status
@app.route('/appointment/<string:status>', methods=['GET'])
@jwt_required()
def all_appointment_status(status):
    
    join = db.session.query(Appointment, Pet, Owner).join(Pet, Appointment.owner_id == Pet.owner_id).join(Owner, Appointment.owner_id == Owner.id).filter(Appointment.status == status).all()

    if join:
        results = [{
            'pet_profile': pet.profile.decode() if pet else None,
            'pet_name': pet.name if pet else None,
            'owner_first_name': owner.first_name if owner else None,
            'owner_last_name': owner.last_name if owner else None,
            'appointment_date': appointment.date if appointment else None,
            'appointment_time': appointment.time if appointment else None
        } for appointment, pet, owner in join]

        return jsonify(results), 200

    return jsonify([]), 200

#POST/ADD appointment 
@app.route('/pet/<int:pet_id>/appointment', methods=['POST'])
@jwt_required()
def add_appointment(pet_id):
    try:
        owner_id = get_jwt_identity()
        record_id = request.form['record_id']

        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        status = request.form['status']

        appointment = Appointment(pet_id = pet_id, owner_id = owner_id, record_id = record_id, title = title, date = date, time = time, status = status)

        db.session.add(appointment)
        db.session.commit()

        response = {
            "message": "The Appointment is added"
        }

        return jsonify(response), 201

    except (KeyError, TypeError):
        response = {
            "error": "Invalid Data"
        }
        
        return jsonify(response), 400

#PUT/EDIT appointment
@app.route('/pet/appointment/<int:appointment_id>/update', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    try:
        appointment = Appointment.query.filter_by(id=appointment_id).first()
        if appointment:
            appointment.title = request.form['title']
            appointment.date = request.form['date']
            appointment.time = request.form['time']
            
            db.session.commit()
            response = { "message": "Successfully Update" }

            return jsonify(response), 200

    except (ValueError, TypeError):
        response = {
            "error" : "Invalid data"
        }

        return jsonify(response), 400

#DELETE appointment
@app.route('/pet/appointment/<int:appointment_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    try:

        appointment = Appointment.query.filter_by(id=appointment_id).first()
        if appointment:
            db.session.delete(appointment)            
            db.session.commit()
            response = {
                "message": "Successfully Delete"
            }

            return jsonify(response), 200

        else:
            response = {
                "message": "Appointment Not Found"
            }

            return jsonify(response), 404

    except (ValueError, TypeError):
        response = {
            "error" : "Invalid data"
        }

        return jsonify(response), 400

# ===========VET========================================================================================================================

#GET list of owners
@app.route('/owners', methods=['GET'])
@jwt_required()
def all_owner():
    owners = Owner.query.all()

    response = owners_schema.dump(owners)
    return jsonify(response), 200

#GET list of vets
@app.route('/vets', methods=['GET'])
@jwt_required()
def all_vet():
    vets = Vet.query.all()

    return jsonify(vets), 200

#Add Vet
@app.route('/add/vet', methods=['POST'])
def add_vet():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email_address = request.form['email_address']
    password = request.form['password']

    if not first_name or not last_name or not email_address or not password:
        response = {
            "error": "Please input field"
        }

        return jsonify(response), 400

    existing_email = Vet.query.filter_by(email_address=email_address).first()

    if existing_email:
        response = {
            "error": "Email already exists"
        }

        return jsonify(response), 400

    vet = Vet(first_name = first_name, last_name = last_name, email_address = email_address)
    vet.set_password(password)

    db.session.add(vet)
    db.session.commit()

    access_token = create_access_token(identity = vet.id)
    response = {
        "message": "You registered successfully.",
        "access_token": access_token
    }

    return jsonify(response), 201

# ===========ADMIN======================================================================================================================

#DELETE owner account
@app.route('/owner/<int:owner_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_owner(owner_id):
    try:
        admin_id = get_jwt_identity()

        # owner = Owner.query.filter_by(owner_id=owner_id, id=admin_id).first()
        owner = Owner.query.filter_by(id=owner_id).first()
        if owner:
            db.session.delete(owner)            
            db.session.commit()
            response = {
                "message": "Successfully Delete"
            }

            return jsonify(response), 200

        else:
            response = {
                "message": "User Not Found"
            }

            return jsonify(response), 404

    except (ValueError, TypeError):
        response = {
            "error" : "Invalid data"
        }

        return jsonify(response), 400

# Run Server
if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)