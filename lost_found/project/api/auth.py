from sqlalchemy import exc, or_
from project.models.models import Users
from project import db, bcrypt
from project.api.utils import authenticate
from flask import jsonify, request, Blueprint, url_for
from project.token import generate_confirmation_token, confirm_token
from project.email import send_email

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/test', methods=['GET'])
def test_endpoint():
    response_object = {
        'status': 'success',
        'message': 'Tested V1.1'
    }
    return jsonify(response_object), 200


@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user():
    """
    Input: json object
        {

            'firstname':  user's firstname,
            'lastname': user's lastname,
            'email' : user email address,
            'phone' : user phone nimber
            'password' : user password,
            'item_pic': base64 string value for item picture

        }
    """
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    firstname = post_data.get('firstname')
    lastname = post_data.get('lastname')
    email = post_data.get('email')
    phone = post_data.get('phone')
    password = post_data.get('password')

    if not email or not password or not firstname or not phone:
        return jsonify(response_object), 400

    try:
        # check for existing user
        user = Users.query.filter(Users.email == email).first()
        # checking for unique phone numbers as we need them for
        user_phone = Users.query.filter(Users.phone == phone).first()
        if user_phone:
            response_object["message"] = "A user with this phone number already exists"
            return jsonify(response_object), 400
        if not user:
            new_user = Users(
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                password=password,
                confirmed=False
            )
            db.session.add(new_user)
            db.session.commit()
            auth_token = new_user.encode_auth_token(new_user.id)
            response_object['status'] = 'success'
            response_object['message'] = 'Successfully registered.'
            response_object['auth_token'] = auth_token.decode()
            # token = generate_confirmation_token(new_user.email)
            # confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            # content = confirm_url
            # subject = "Please confirm your email"
            # send_email(new_user.email, subject, content)
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That user already exists.'
            return jsonify(response_object), 400
    # handler errors
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object['message'] = "Internal server error"
        return jsonify(response_object), 400


@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user():
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        # fetch the user data
        user = Users.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response_object['status'] = 'success'
                response_object['message'] = 'Successfully logged in.'
                response_object['auth_token'] = auth_token.decode()
                return jsonify(response_object), 200
        else:
            response_object['message'] = 'User does not exist.'
            return jsonify(response_object), 404
    except Exception as e:
        print(e)
        response_object['message'] = 'Try again'
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
def logout_user():
    auth_header = request.headers.get('Authorization')
    response_object = {
        'status': 'fail',
        'message': 'provide a valide auth token.'
    }
    if auth_header:
        auth_token = auth_header.split('')
        resp = Users.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            response_object['status'] = 'success'
            response_object['message'] = 'Successfully logged out.'
            return jsonify(response_object), 200
        else:
            response_object['message'] = resp
            return jsonify(response_object), 401
    else:
        return jsonify(response_object), 403


@auth_blueprint.route('/auth/change-password/<user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    post_data = request.get_json()
    new_password = post_data.get()
    try:
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.password = bcrypt.generate_password_hash(new_password, current_app.config.get('BCRYPT_LOG_ROUNDS')
                                                          ).decode()
            response_object['message'] = 'password was update successfully'
            return jsonify(response_object), 200
        else:
            return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object['message'] = "Internal server error"
        return jsonify(response_object), 400


@auth_blueprint.route('/auth/confirm/<token>')
def confirm_email(token):
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    try:
        email = confirm_token(token)
    except:
        response_object['message'] = 'The confirmation link is invalid or has expired.', 'danger'
    user = Users.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        response_object['message'] = 'Account already confirmed. Please login.', 'success'
        return jsonify(response_object), 200
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        response_object['message'] = 'Account confirmed'
        return jsonify(response_object), 201
