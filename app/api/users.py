from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User
from app.api.auth import verify_request
from app.api.errors import error_response

import json


@bp.route('/user/exists', methods=['GET'])
def check_user_exists():
    try:
        params = request.args
        exist_response = dict()

        if 'email' not in params or 'phoneNumber' not in params:
            return error_response(400)

        user_by_email = User.query.filter_by(email=params['email']).first()
        if user_by_email != None:
            exist_response['exists'] = True
            exist_response['emailExists'] = True

        user_by_phone = User.query.filter_by(phone_number=params['phoneNumber']).first()
        if user_by_phone != None:
            exist_response['exists'] = True
            exist_response['phoneExists'] = True

        return jsonify(exist_response), 200
    except Exception as e:
        print(str(e))
        return error_response(500)


@bp.route('/user/create', methods=['POST'])
def create_user():
    try:
        request_data = json.loads(request.data)
        if ('firstName' not in request_data or
            'lastName' not in request_data or
            'email' not in request_data or
            'phoneNumber' not in request_data or
            'password' not in request_data):
            return error_response(400)

        user = User()
        user.from_dict(request_data, new_user=True)
        db.session.add(user)
        db.session.commit()

        response = jsonify(user.to_dict())
        response.status_code = 201
        return response

    except Exception as e:
        return error_response(500)
