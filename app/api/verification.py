from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.api.errors import error_response

from twilio.rest import Client

import json


@bp.route('/verification/create', methods=['POST'])
def send_verification():
    try:
        # Loads the request data into a json object and
        # Validates that the correct fields are included
        request_data = json.loads(request.data)
        if 'channel' not in request_data or 'address' not in request_data:
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Creates and sends the verification code to the user at the specified channel and address
        verification = __create_verification(request_data['channel'], request_data['address'])

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

@bp.route('/verification/check', methods=['POST'])
def check_verification():
    try:
        # Loads the request data into a json object and
        # Validates that the correct fields are included
        request_data = json.loads(request.data)
        if 'address' not in request_data or 'code' not in request_data:
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Checks the verification code for the user at the specified address and code
        verification_check = __check_verification_status(request_data['address'], request_data['code'])

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


def __create_verification(channel, address):
    # Gets the twilio client
    client = __get_client()

    # Sends the verification code to the address specified in the function. To find out what this returns,
    # Go to https://www.twilio.com/docs/verify/api/verification#verification-response-properties to get more information on the object
    verification = client.verify.services(current_app.config['TWILIO_SERVICE_ID']).verifications.create(to=address, channel=channel)

    # Returns the verification object
    return verification

def __check_verification_status(address, code):
    # Gets the twilio client
    client = __get_client()

    # Checks the verification code for the address specified in the function. To find out what this returns,
    # Go to https://www.twilio.com/docs/verify/api/verification-check#check-a-verification to get more information on the object
    verification_check = client.verify.services(current_app.config['TWILIO_SERVICE_ID']).verification_checks.create(to=address, code=code)

    # Returns the verification check object
    return verification_check

def __get_client():
    # Creates and returns a client based on the twilio config details
    return Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
