from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User, Settings
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims, jwt_refresh_token_required
from sqlalchemy import desc, asc

import json
from datetime import datetime

@bp.route('/settings', methods=['GET', 'POST'])
@verify_request
def settings():
    try:
        # Gets the full phone number
        full_phone_number = get_jwt_identity()

        # Checks the method being passed through to the API
        if request.method == 'GET':
            # Sets the global parameter
            global date
            # Gets the request string
            date_param = request.args.get('date', None)

            # Checks if the date exists in the request
            if not date_param:
                date = datetime.today().strftime('%Y-%m')
            else:
                date = date_param

            # Gets the settings
            settings = get_settings(full_phone_number, date)

            # Creates the object to send in the response
            # and returns the response
            response = {
                'settings': settings
            }
            return jsonify(response), 200
        else:
            return __create_settings(full_phone_number, json.loads(request.data))
    except Exception as e:
        # logs the error
        current_app.logger.fatal(str(e))
        # Returns a 500 response (Internal Server Error)
        return error_response(500)

def get_settings(full_phone_number, date):
    '''
    Gets the users settings based on the full phone number
    '''

    try:
        # Gets the settings based on the full_phone_number
        settings = Settings.query.filter(Settings.effective_at <= datetime.strptime(date, '%Y-%m')).join(Settings.user).filter(User.full_phone_number == full_phone_number).order_by(desc(Settings.effective_at)).first()

        # Checks if there are any settings
        # If not, we return a 403
        if not settings:
            return {}

        # Returns the json format of the settings object
        return settings.to_dict()
    except Exception as e:
        # logs the error
        current_app.logger.fatal(str(e))
        # raises the error so that the caller can return 500
        raise

def __create_settings(full_phone_number, request_data):
    '''
    Creates a settings entry for the user

    If there exists a settings entry for that specified effective_at date, we
    delete the entry and add the new one

    Because we want to maintain a full history of all incomes set, we do not
    update any existing entries. Only if there are two with the same effective
    date do we delete and re enter
    '''

    try:
        # Checks if there exists an entry with the same effective date
        settings_for_effective_date = Settings.query.filter(Settings.effective_at == datetime.strptime(request_data['effectiveAt'], '%Y-%m')).first()

        # Checks if settings exist
        # If so, we delete the settings from the session
        if settings_for_effective_date:
            db.session.delete(settings_for_effective_date)

        # Once we delete, we then get the user to attach to the settings
        user = User.query.filter(User.full_phone_number == full_phone_number).first()

        # After we get the user, we make the entry
        # and read in from the request data
        settings = Settings()
        settings.from_dict(request_data, user)

        # After getting the entry, we add it to the session
        db.session.add(settings)
        current_app.logger.info('added settings for {0} to the database session'.format(settings.user))

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited settings to the database session')

        # Returns the response with status code 201 to indicate the user has been created
        return error_response(201)
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        raise
