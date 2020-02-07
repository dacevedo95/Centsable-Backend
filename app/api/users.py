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
        # Gets the parameters for the call and
        # Checks whether the 'phoneNumber' parameter has been included and is not empty
        params = request.args
        if 'phoneNumber' not in params or params['phoneNumber'] == "" or params['phoneNumber'] == None:
            current_app.logger.error('phoneNumber not included in request arguements: {0}'.format(params))
            return error_response(400)

        # Builds the initial response object and
        # Pulls the phone number from the request parameters
        exist_response = {
            'exists': False
        }
        phone_number_input = params['phoneNumber']
        current_app.logger.info('Checking if user with phone number {0} exists'.format(phone_number_input))

        # Makes a call against the database to find a user based on the phone number filter and
        # Sets the response object field 'exists' to True if a user is found
        user_by_phone = User.query.filter_by(phone_number=params['phoneNumber'])
        if user_by_phone.first() != None:
            exist_response['exists'] = True

        # Logs whether a user has been found and
        # Returns the response
        current_app.logger.info('Found {0} user(s) with phone number {1}'.format(user_by_phone.count(), phone_number_input))
        return jsonify(exist_response), 200
    except Exception as e:
        # Logs the response and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
        return error_response(500)


@bp.route('/user/create', methods=['POST'])
def create_user():
    try:
        # Loads the request body into a json format and
        # Checks if all required parameters are included in the request
        request_data = json.loads(request.data)
        if ('firstName' not in request_data or
            'lastName' not in request_data or
            'phoneNumber' not in request_data or
            'password' not in request_data):
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Creates a User object and creates the user from the request body json
        user = User()
        user.from_dict(request_data, new_user=True)

        # Logs that the user is being added to the database and then adds to the database
        # We will commit later once everything has been processed correctly
        db.session.add(user)
        current_app.logger.info('added user with phone number {0} to the database session'.format(user.phone_number))

        # Formats the request response to a json format to be returned in the response
        response = jsonify(user.to_dict())

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited user with phone number {0} to the database session'.format(user.phone_number))

        # Returns the response with status code 201 to indicate the user has been created
        return response, 201
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        return error_response(500)
