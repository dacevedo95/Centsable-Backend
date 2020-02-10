from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User
from app.api.auth import verify_request
from app.api.errors import error_response

import json

from twilio.rest import Client


@bp.route('/users/<phone_number>/exists', methods=['GET'])
def check_user_exists(phone_number):
    try:
        # Gets the parameters for the call and
        # Checks whether the 'phoneNumber' parameter has been included and is not empty
        if phone_number == None or phone_number == '':
            current_app.logger.error('phoneNumber not included in request arguements: {0}'.format(params))
            return error_response(400)

        # Builds the initial response object and
        # Pulls the phone number from the request parameters
        exist_response = {
            'exists': False
        }
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
def create_user():
    try:
        # Loads the request body into a json format and
        # Checks if all required parameters are included in the request
        request_data = json.loads(request.data)
        if ('firstName' not in request_data or
            'lastName' not in request_data or
            'password' not in request_data):
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
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
        current_app.logger.info('commited user user {0} {1} to the database session'.format(user.first_name, user.last_name))

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

@bp.route('/users/verification/check', methods=['GET'])
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
        # If the status is anything else, we throw an exception
        if verification_check.status == 'approved':
            current_app.logger.info('verified user with phone number {0} and status {1}'.format(verification_check.to, verification_check.status))
            return error_response(204)
        else:
            raise Exception('could not check verification, status is {0}'.format(verification_check.status))
    except Exception as e:
        # Logs the exception when it happens and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
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
