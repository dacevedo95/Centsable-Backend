from flask import jsonify, g, request, current_app
from app import db
from app.models import User
from app.api import bp
from app.api.auth import verify_refresh_request

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

import time

@bp.route('/login', methods=['POST'])
def get_token():
    """
    This endpoint is used for users to get bearer tokens

    This request receives a email and password for login purposes, and uses the auth.verify_password function in the
    'auth' module. If the return is True (email and password are correct), we then call the get token method to retrieve
    the existing token, or generate a new one if it is expiring or expired
    """

    # Checks if there is a body
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    # Gets the username and password, and defaults to null
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    # Validation in case the user didn't include anything
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # Tries to find a user by the given email
    user = User.query.filter_by(email=email).first()
    # Returns false if the user does not exist
    if user is None or not user.check_password(password):
        return jsonify({"msg": "Email or password is incorrect"}), 400

    # Generates the access token
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    # Returns the access token
    return jsonify({
        'token': access_token,
        'expires_at': int(time.time()) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] - 1,
        'refresh_token': refresh_token
    }), 200

@bp.route('/refresh', methods=['GET'])
@verify_refresh_request
def refresh_token():
    current_user = get_jwt_identity()
    return jsonify({
        'token': create_access_token(identity=current_user),
        'expires_at': int(time.time()) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] - 1,
        'refresh_token': create_refresh_token(identity=current_user)
    }), 200
