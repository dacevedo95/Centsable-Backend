from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User, RecurringTransaction
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims, jwt_refresh_token_required

import json
from datetime import datetime


@bp.route('/overview', methods=['GET'])
@verify_request
def get_overview():
    # Checks if a date has been passed through
    # if not, we default to todays month and year
    date_param = request.args.get('date', None)
    if not date_param:
        # Gets the current date in YYYY-MM format
        date_today = datetime.today().strftime('%Y-%m')
        return __get_overview(None)
    else:
        pass


def __get_overview(date, is_past_date=False):
    pass
