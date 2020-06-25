from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User, Transaction, RecurringTransaction
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims, jwt_refresh_token_required
from sqlalchemy import and_

import json
from datetime import datetime


@bp.route('/transactions', methods=['GET', 'POST'])
@verify_request
def transactions():
    # Checks the method being passed through to the API
    if request.method == 'GET':
        # Gets the date flag from the URL
        # If no date is specified, we pass through todays date
        date_string = request.args.get('date', None)

        # Checks if the date string is None
        # If so, return a 400 error
        if not date_string:
            current_app.logger.error('Date not provided for the /transactions endpoint')
            return error_response(400)

        # Loads the date into a datetime object
        date = datetime.strptime(date_string, '%Y-%m')

        # Executes/Returns the data need whether it is recurring or non-recurring
        return __get_transactions(get_jwt_identity(), date)
    # The else statement means that it is a POST request
    # In this case, we create a transaction
    else:
        return __create_transactions(get_jwt_identity(), json.loads(request.data))

@bp.route('/transactions/<id>', methods=['PUT', 'DELETE'])
@verify_request
def update_transaction(id):
    if request.method == 'PUT':
        return __update_transaction(id, get_jwt_identity(), json.loads(request.data))
    else:
        return __delete_transaction(id, get_jwt_identity())


def __create_transactions(full_phone_number, request_data):
    try:
        # Loads the request body
        # and checks whether all information is present
        if ('transactions' not in request_data):
            current_app.logger.error('request body not formatted correctly, body is missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Gets the identity of the JWT
        # and gets the user from the DB
        author = User.query.filter(User.full_phone_number == full_phone_number).first()

        # Gets the list of transactions
        # And creates transactions for that User
        transactions_list = request_data['transactions']
        for item in transactions_list:
            # Makes sure that the data is formatted correctly
            if ('name' not in item or
                'category' not in item or
                'price' not in item or
                'createdAt' not in item):
                current_app.logger.error('transaction not formatted correctly, missing required parameters: {0}'.format(item))
                return error_response(400)

            # Creates the new Transaction
            # and attaches the author to it
            transaction = Transaction()
            transaction.from_dict(item, author=author)

            # Logs that the user is being added to the database and then adds to the database
            # We will commit later once everything has been processed correctly
            db.session.add(transaction)
            current_app.logger.info('added transaction {0} {1} to the database session'.format(transaction.category, transaction.name))

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited transactions to the database session')

        # Returns the response with status code 201 to indicate the user has been created
        return error_response(201)
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        return error_response(500)


def __get_transactions(full_phone_number, date):
    try:
        # Gets both the monthly transactions
        # and the recurring payments
        transactions_by_month = Transaction.query.filter(Transaction.created_at >= date, Transaction.created_at < date.replace(month=date.month+1)).join(Transaction.author).filter(User.full_phone_number == full_phone_number)
        recurring_transactions_by_user = RecurringTransaction.query.join(RecurringTransaction.recurring_author).filter(User.full_phone_number == full_phone_number)

        # Initializes local variables for the return json
        transactions = []
        recurring_transactions = []
        amount_spent = 0

        # Loops through all transactions and puts them in a list
        # Also adds up the sum of transactions
        for transaction in transactions_by_month:
            amount_spent += transaction.price
            transactions.append(transaction.to_dict())

        # Loops through all transactions and puts them in a list
        # Continues to add up the values
        for recurring_transaction in recurring_transactions_by_user:
            amount_spent += recurring_transaction.price
            recurring_transactions.append(recurring_transaction.to_dict())

        # returns the jsonified version
        return jsonify({
            'amountSpent': round(amount_spent, 2),
            'recurringTransactions': recurring_transactions,
            'transactions': transactions
        }), 200
    except Exception as e:
        # Logs the response and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
        return error_response(500)


def __update_transaction(id, full_phone_number, request_data):
    try:
        # Loads the request data
        # and makes sure all fields are there
        if ('name' not in request_data or
            'category' not in request_data or
            'price' not in request_data or
            'createdAt' not in request_data):
            current_app.logger.error('request data not formatted correctly, missing required parameters: {0}'.format(request_data))
            return error_response(400)

        # Loads the user from the identity in the JWT
        # and queries the database
        transaction = Transaction.query.filter(Transaction.id == id).join(Transaction.author).filter(User.full_phone_number == full_phone_number).first()

        # checks if the row exists
        if not transaction:
            return error_response(403)

        # updates all fields in the transaction
        transaction.from_dict(request_data)

        # Adds the transaction to the session
        db.session.add(transaction)
        current_app.logger.info('added transaction {0} {1} to the database session'.format(transaction.category, transaction.name))

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited transactions to the database session')

        return error_response(204)
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        return error_response(500)


def __delete_transaction(id, full_phone_number):
    try:
        # Loads the user from the identity in the JWT
        # and queries the database
        transaction = Transaction.query.filter(Transaction.id == id).join(Transaction.author).filter(User.full_phone_number == full_phone_number).first()

        # checks if the row exists
        if not transaction:
            return error_response(403)

        # deletes the transaction from the session
        db.session.delete(transaction)
        current_app.logger.info('deleted transaction {0} {1} to the database session'.format(transaction.id, transaction.name))

        # Commits the user to the database and logs that is has been commited
        db.session.commit()
        current_app.logger.info('commited transactions to the database session')

        return error_response(204)
    except Exception as e:
        # Logs the exception that has been raised and rolls back all the changes made
        current_app.logger.fatal(str(e))
        db.session.rollback()
        # Returns a 500 response (Internal Server Error)
        return error_response(500)
