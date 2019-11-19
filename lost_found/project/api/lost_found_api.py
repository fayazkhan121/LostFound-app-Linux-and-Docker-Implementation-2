from random import randint
from sqlalchemy import exc, or_
from project.models.models import Users, Items
from project.api.utils import authenticate
from flask import jsonify, request, Blueprint
from project import db, bcrypt

lost_found_blueprint = Blueprint('lost_found', __name__)


@lost_found_blueprint.route('/lost_found/test', methods=['GET'])
def test_endpoint():
    response_object = {
        'status': 'success',
        'message': 'Test'
    }
    return jsonify(response_object), 200


@lost_found_blueprint.route('/lost_found/item/create', methods=['POST'])
def create_item():
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    post_data = request.get_json()
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    category = post_data.get('category')
    location = post_data.get('location')
    description = post_data.get('description')
    item_pic = post_data.get('item_pic')
    try:
        item = Items.query.filter(Items.name == name and Items.location == location).first()
        if item:
            response_object['message'] = 'This lost item is already registered in the system'
            return jsonify(response_object), 400
        else:
            new_item = Items(
                name=name,
                category=category,
                location=location,
                description=description,
                item_pic=item_pic)
            db.session.add(new_item)
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Successfully created.'
            return jsonify(response_object), 201
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object['message'] = "Internal server error"
        return jsonify(response_object), 400


@lost_found_blueprint.route('/lost_found/item/update/<item_id>', methods=['PUT'])
def update_item(item_id):
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    post_data = request.get_json()
    if not post_data:
        return jsonify(response_object), 400
    try:
        item = Items.query.filter_by(id=item_id).first()
        if not item:
            response_object['message'] = 'item does not exist'
            return jsonify(response_object), 401
        else:
            item.name = post_data.get('name')
            item.category = post_data.get('category')
            item.location = post_data.get('location')
            item.description = post_data.get('description')
            item.item_pic = post_data.get('item_pic')
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Item was updated!'
            return jsonify(response_object), 200
    except (exc.IntegrityError, ValueError, TypeError) as e:
        db.session().rollback()
        return jsonify(response_object), 400


@lost_found_blueprint.route('/lost_found/item/list', methods=['GET'])
def list_item():
    """Get all items"""
    response_object = {
        'status': 'success',
        'data': {
            'scores': [item.item_to_json() for item in Items.query.all()]
        }
    }
    return jsonify(response_object), 200


@lost_found_blueprint.route('/lost_found/item/search/<name>/<location>', methods=['GET'])
def search_item(name, location):
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    try:
        item = Items.query.filter(Items.name == name and
                                  Items.location == location).all()
        if item:
            response_object = {
                'status': 'success',
                'data': {
                    'items': [i.item_to_json() for i in item]
                    }
                }
            return jsonify(response_object), 200
        else:
            response_object['message'] = 'No item found for this name and location'
            return jsonify(response_object), 401
    except (exc.IntegrityError, ValueError, TypeError) as e:
        db.session().rollback()
        return jsonify(response_object), 400


@lost_found_blueprint.route('/lost_found/item/delete/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    response_object = {
        'status': 'fail',
        'message': 'item does not exist'
    }
    try:
        item = Items.query.filter_by(id=int(item_id)).first()
        if not item:
            return jsonify(response_object), 404
        else:
            db.session.delete(item)
            db.session.commit()
            response_object = {
                'status': 'deleted',
                'message': 'item delete successful'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 400
