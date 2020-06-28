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
    date_param = request.args.get('date', None)

    # Gets today's YYYY-MM as a string to use later on
    date_today = datetime.today().strftime('%Y-%m')

    # if the date was not passed we get today's YYYY-MM
    # and set is_curent to True
    if not date_param:
        return __get_overview(date_today, is_current=True)
    else:
        # If the date was set, we first need to check if it is todays YYYY-MM
        # If so, then sick
        if date_today == date_param:
            return __get_overview(date_today, is_current=True)
        else:
            return __get_overview(date_param, is_current=False)


def __get_overview(date, is_current=False):
    '''
    Per the designs, we will pass back:
        - A header ("Hello, David", "Well Done", "Over Budget")
        - Total Amount Spent
        - Total Income
        - Show Info
        - Spending
            - Needs (spent, allowed, percentage)
            - Wants (spent, allowed, percentage)
            - Savings (spent, allowed, percentage)
    '''

    # Formats the response
    response = {
        "header": "",
        "amountSpent": 0,
        "monthlyIncome": 0
    }

    pass
