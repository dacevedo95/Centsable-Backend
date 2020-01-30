from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.api.errors import error_response

from twilio.rest import Client

import json


@bp.route('/verify/create', methods=['POST'])
def send_verification():
    try:
        request_data = json.loads(request.data)
        if 'channel' not in request_data or 'address' not in request_data:
            return error_response(400)

        verification = create_verification(request_data['channel'], request_data['address'])
        if verification.status == 'pending':
            return error_response(204)
        else:
            return error_response(500)

    except Exception as e:
        print(str(e))
        return error_response(500)

@bp.route('/verify/check', methods=['POST'])
def check_verification():
    try:
        request_data = json.loads(request.data)
        if 'address' not in request_data or 'code' not in request_data:
            return error_response(400)

        verification_check = check_verification_status(request_data['address'], request_data['code'])
        if verification_check.status == 'approved':
            return error_response(204)
        else:
            return error_response(500)
    except Exception as e:
        print(str(e))
        error_response(500)


def create_verification(channel, address):
    client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
    verification = client.verify.services(current_app.config['TWILIO_SERVICE_ID']).verifications.create(to=address, channel=channel)
    return verification

def check_verification_status(address, code):
    client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
    verification_check = client.verify.services(current_app.config['TWILIO_SERVICE_ID']).verification_checks.create(to=address, code=code)
    return verification_check
