from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User, Transaction, RecurringTransaction, Settings
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims, jwt_refresh_token_required
from app.api.settings import get_settings

import json
import sys
import calendar

from datetime import datetime


@bp.route('/overview', methods=['GET'])
@verify_request
def get_overview():
    # Checks if a date has been passed through
    date_param = request.args.get('date', None)

    # Gets today's YYYY-MM as a string to use later on
    date_today = datetime.today().strftime('%Y-%m')
    # Gets the users full phone number
    full_phone_number = get_jwt_identity()

    # if the date was not passed we get today's YYYY-MM
    # and set is_curent to True
    if not date_param:
        return __get_overview(full_phone_number, date_today, is_current=True)
    else:
        # If the date was set, we first need to check if it is todays YYYY-MM
        # If so, then sick
        if date_today == date_param:
            return __get_overview(full_phone_number, date_today, is_current=True)
        else:
            return __get_overview(full_phone_number, date_param, is_current=False)


def __get_overview(full_phone_number, date, is_current=False):
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

    try:
        # Formats the response to be refilled later
        response = {
            "header": "",
            "amountSpent": 0,
            "monthlyIncome": 0,
            "totalPercentage": 0,
            "daysLeft": 0,
            "showInfo": False,
            "showTransactions": False,
            "settings": {
                "needs": {
                    "spent": 0,
                    "allowed": 0,
                    "percentage": 0
                },
                "wants": {
                    "spent": 0,
                    "allowed": 0,
                    "percentage": 0
                },
                "savings": {
                    "spent": 0,
                    "allowed": 0,
                    "percentage": 0
                }
            }
        }

        # Makes the call to get the users settings for that month
        # And sets the response object
        settings = get_settings(full_phone_number, date)
        response['monthlyIncome'] = settings['income']

        # Reformats the date
        date = datetime.strptime(date, '%Y-%m')

        # Checks what link to show on the app
        if is_current:
            response['showInfo'] = True
        else:
            response['showTransactions'] = True

        # Gets both the monthly transactions
        # and the recurring payments
        transactions_by_month = Transaction.query.filter(Transaction.created_at >= date, Transaction.created_at < date.replace(month=date.month+1)).join(Transaction.author).filter(User.full_phone_number == full_phone_number)
        recurring_transactions_by_user = RecurringTransaction.query.filter(RecurringTransaction.effective_at < date.replace(month=date.month+1)).join(RecurringTransaction.recurring_author).filter(User.full_phone_number == full_phone_number)

        # Initializes the variables
        needs_spent = 0
        wants_spent = 0
        savings_spent = 0

        # Loops through the transactions to get the totals
        for transaction in transactions_by_month:
            if transaction.category == 'Needs':
                response['settings']['needs']['spent'] += transaction.price
            elif transaction.category == 'Wants':
                response['settings']['wants']['spent'] += transaction.price
            else:
                response['settings']['savings']['spent'] += transaction.price

        # Loops through the recurring transactions to get the totals
        for recurring_transaction in recurring_transactions_by_user:
            if recurring_transaction.category == 'Needs':
                response['settings']['needs']['spent'] += recurring_transaction.price
            elif recurring_transaction.category == 'Wants':
                response['settings']['wants']['spent'] += recurring_transaction.price
            else:
                response['settings']['savings']['spent'] += recurring_transaction.price

        # Gets the allowed for each category
        response['settings']['needs']['allowed'] = settings['income'] * settings['needsPercentage']
        response['settings']['wants']['allowed'] = settings['income'] * settings['wantsPercentage']
        response['settings']['savings']['allowed'] = settings['income'] * settings['savingsPercentage']

        # Gets the percentaage for each category
        response['settings']['needs']['percentage'] = (response['settings']['needs']['spent'] / response['settings']['needs']['allowed']) * 100
        response['settings']['wants']['percentage'] = (response['settings']['wants']['spent'] / response['settings']['wants']['allowed']) * 100
        response['settings']['savings']['percentage'] = (response['settings']['savings']['spent'] / response['settings']['savings']['allowed']) * 100

        # Calculates the amount spent
        response['amountSpent'] = response['settings']['needs']['spent'] + response['settings']['wants']['spent'] + response['settings']['savings']['spent']

        # Gets the total percentage
        response['totalPercentage'] = (response['amountSpent'] / response['monthlyIncome']) * 100

        # Gets the number of days left
        now = datetime.now()
        response['daysLeft'] = calendar.monthrange(now.year, now.month)[1] - now.day + 1

        # If it is not current we set the header
        if not is_current:
            if response['amountSpent'] > response['monthlyIncome']:
                response['header'] = 'Over Budget'
            else:
                response['header'] = 'Well Done!'
        else:
            # Gets the User so that we can get their first name
            user = User.query.filter(User.full_phone_number == full_phone_number).first()
            # Sets the header
            response['header'] = 'Hello, ' + user.first_name

        return jsonify(response), 200
    except Exception as e:
        # Logs the response and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal('Error on line {0} {1}'.format(sys.exc_info()[-1].tb_lineno, str(e)))
        return error_response(500)
