from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import and_

import json
import time

from twilio.rest import Client


@bp.route('/users/exists', methods=['POST'])
def check_user_exists():
    try:
        # Gets the parameters for the call and
        # Checks whether the 'phoneNumber' parameter has been included and is not empty
        request_data = json.loads(request.data)
        if 'phoneNumber' not in request_data or 'countryCode' not in request_data:
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Builds the initial response object and
        # Pulls the phone number from the request parameters
        exist_response = {
            'exists': False
        }
        phone_number = request_data['phoneNumber']
        current_app.logger.info('Checking if user with phone number {0} exists'.format(phone_number))

        # Makes a call against the database to find a user based on the phone number filter and
        # Sets the response object field 'exists' to True if a user is found
        user_by_phone = User.query.filter_by(phone_number=phone_number)
        if user_by_phone.first() != None:
            exist_response['exists'] = True

        # Logs whether a user has been found and
        # Returns the response
        current_app.logger.info('Found {0} user(s) with phone number {1}'.format(user_by_phone.count(), phone_number))
        return jsonify(exist_response), 200
    except Exception as e:
        # Logs the response and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
        return error_response(500)


@bp.route('/users', methods=['POST'])
@jwt_required
def create_user():
    try:
        # Loads the request body into a json format and
        # Checks if all required parameters are included in the request
        request_data = json.loads(request.data)
        if ('firstName' not in request_data or
            'lastName' not in request_data or
            'password' not in request_data or
            'phoneNumber' not in request_data or
            'countryCode' not in request_data):
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Checks if the JWT identity is the same as the one being created
        identity = get_jwt_identity()
        if identity != "+" + request_data['countryCode'] + request_data['phoneNumber']:
            current_app.logger.error('identity {0} doesnt match phone number +{1}{2}'.format(identity, request_data['countryCode'], request_data['phoneNumber']))
            return error_response(400)

        # Creates a User object and creates the user from the request body json
        user = User()
        user.from_dict(request_data, new_user=True)

        # Logs that the user is being added to the database and then adds to the database
        # We will commit later once everything has been processed correctly
        db.session.add(user)
        current_app.logger.info('added user {0} {1} to the database session'.format(user.first_name, user.last_name))

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited user {0} {1} to the database session'.format(user.first_name, user.last_name))

        # Returns the response with status code 201 to indicate the user has been created
        return error_response(201)
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        return error_response(500)


@bp.route('/users/verification', methods=['POST'])
def send_verification():
    try:
        # Loads the request data into a json object and
        # Validates that the correct fields are included
        request_data = json.loads(request.data)
        if 'countryCode' not in request_data or 'phoneNumber' not in request_data:
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Creates and sends the verification code to the user at the specified channel and address
        verification = __create_verification('sms', request_data['countryCode'], request_data['phoneNumber'])

        # Checks the status of the verification being sent. We look for a status of 'pending'.
        # If the status is anything else, we throw an exception
        if verification.status == 'pending':
            current_app.logger.info('sent verification with status {0} to {1}'.format(verification.status, verification.to))
            return error_response(204)
        else:
            raise Exception('could not create verification, status is {0}'.format(verification.status))
    except Exception as e:
        # Logs the exception when it happens and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
        return error_response(500)


@bp.route('/users/verification/check', methods=['POST'])
def check_verification():
    try:
        # Loads the request data into a json object and
        # Validates that the correct fields are included
        request_data = json.loads(request.data)
        if 'phoneNumber' not in request_data or 'code' not in request_data or 'countryCode' not in request_data:
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Checks the verification code for the user at the specified address and code
        verification_check = __check_verification_status(request_data['countryCode'], request_data['phoneNumber'], request_data['code'])

        # Checks the verification status received. We look for a status of 'approved'.
        # Once approved, we update the users profile in the database
        # If the status is anything else, we throw an exception
        if verification_check.status == 'approved':
            current_app.logger.info('verified user with phone number {0} and status {1}'.format(verification_check.to, verification_check.status))

            # Creates the access token and the refresh token with identity equal to the key in the database
            access_token = create_access_token(identity=verification_check.to)
            refresh_token = create_refresh_token(identity=verification_check.to)

            # Returns the response with status code 201 to indicate the user has been created
            return jsonify({
                'token': access_token,
                'expires_at': int(time.time()) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] - 1,
                'refresh_token': refresh_token
            }), 200
        else:
            current_app.logger.error('phone number {0} was not verified, received status: {1}'.format(verification_check.to, verification_check.status))
            return error_response(400)
    except Exception as e:
        # Logs the exception when it happens and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
        return error_response(500)


@bp.route('/users/reset-password', methods=['POST'])
@jwt_required
def reset_password():
    try:
        # Loads the request body into a json format and
        # Checks if all required parameters are included in the request
        request_data = json.loads(request.data)
        if ('newPassword' not in request_data or
            'phoneNumber' not in request_data or
            'countryCode' not in request_data):
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Checks if the JWT identity is the same as the one being created
        identity = get_jwt_identity()
        if identity != "+" + request_data['countryCode'] + request_data['phoneNumber']:
            current_app.logger.error('identity {0} doesnt match phone number +{1}{2}'.format(identity, request_data['countryCode'], request_data['phoneNumber']))
            return error_response(400)

        # Resets the password
        user = User.query.filter(User.country_calling_code == request_data['countryCode'], User.phone_number == request_data['phoneNumber']).first()
        user.reset_password(newPassword=request_data['newPassword'])

        # Logs that the user is being added to the database and then adds to the database
        # We will commit later once everything has been processed correctly
        db.session.add(user)
        current_app.logger.info('added for country code {0} and phone number {1}'.format(request_data['countryCode'], request_data['phoneNumber']))

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited for country code {0} and phone number {1}'.format(request_data['countryCode'], request_data['phoneNumber']))

        # Returns status code 200
        return error_response(200)
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        return error_response(500)



def __create_verification(channel, country_calling_code, phone_number):
    # Gets the twilio client
    client = __get_client()

    # Constructs the phone number
    full_phone_number = "+" + str(country_calling_code) + str(phone_number)

    # Sends the verification code to the address specified in the function. To find out what this returns,
    # Go to https://www.twilio.com/docs/verify/api/verification#verification-response-properties to get more information on the object
    verification = client.verify.services(current_app.config['TWILIO_SERVICE_ID']).verifications.create(to=full_phone_number, channel=channel)

    # Returns the verification object
    return verification

def __check_verification_status(country_calling_code, phone_number, code):
    # Gets the twilio client
    client = __get_client()

    # Constructs the phone number
    full_phone_number = "+" + str(country_calling_code) + str(phone_number)

    # Checks the verification code for the address specified in the function. To find out what this returns,
    # Go to https://www.twilio.com/docs/verify/api/verification-check#check-a-verification to get more information on the object
    verification_check = client.verify.services(current_app.config['TWILIO_SERVICE_ID']).verification_checks.create(to=full_phone_number, code=code)

    # Returns the verification check object
    return verification_check

def __get_client():
    # Creates and returns a client based on the twilio config details
    return Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
