import datetime
import jwt
from project import db, bcrypt
from flask import current_app


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(32), nullable=False)
    lastname = db.Column(db.String(32))
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(128), unique=True, nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    items = db.relationship("Items", backref=db.backref("Users", uselist=False))

    # Class constructor
    def __init__(self, firstname, lastname, email, password, phone, confirmed, confirmed_on=None):
        self.firstname = firstname,
        self.lastname = lastname,
        self.email = email,
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')
                                                      ).decode()
        self.phone = phone
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    # Returning the class attribute in json format
    def user_to_json(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'confirmed': self.confirmed,
            'confirmed_on': self.confirmed_on
        }

    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                    seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


# lost Item model
class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.String(32), nullable=False)
    category = db.Column(db.String(32), db.Enum('Lost', 'Found'), nullable=True)
    location = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(128), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)
    modified_date = db.Column(db.DateTime, nullable=False)
    item_pic = db.Column(db.String(255), nullable=False)

    # Class constructor
    def __init__(self, name, category, location, description, item_pic):
        self.name = name
        self.category = category
        self.location = location
        self.description = description
        self.create_date = datetime.datetime.utcnow()
        self.modified_date = datetime.datetime.utcnow()
        self.item_pic = item_pic

    # Returning class attribute in a json format
    def item_to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'location': self.location,
            'description': self.description,
            'create_data': self.create_date,
            'modified_data': self.modified_date,
            'item_pic': self.item_pic
        }
