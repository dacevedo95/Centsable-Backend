from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User, Transaction
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims, jwt_refresh_token_required

import json


@bp.route('/transactions', methods=['GET', 'POST'])
@verify_request
def transactions():
    if request.method == 'GET':
        return __get_transactions(get_jwt_identity())
    else:
        return __create_transactions(get_jwt_identity(), json.loads(request.data))


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
                'createdAt' not in item or
                'isRecurring' not in item):
                current_app.logger.error('transaction not formatted correctly, missing required parameters: {0}'.format(item))
                return error_response(400)

            # Creates the new Transaction
            # and attaches the author to it
            transaction = Transaction()
            transaction.from_dict(item, author)

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


def __get_transactions(full_phone_number):
    try:
        # Gets the phone number from the jwt
        # and finds the user with the query
        user = User.query.filter(User.full_phone_number == full_phone_number).first()

        # Gets the list of transactions from the user
        transactions = []
        for transaction in user.transactions:
            transactions.append(transaction.to_dict())

        # returns the jsonified version
        return jsonify({
            'transactions': transactions
        }), 200
    except Exception as e:
        # Logs the response and
        # Returns a 500 response (Internal Server Error)
        current_app.logger.fatal(str(e))
        return error_response(500)
