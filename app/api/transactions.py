from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.models import User, Transaction
from app.api.auth import verify_request
from app.api.errors import error_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_claims, jwt_refresh_token_required

@bp.route('/transactions', methods=['GET'])
@verify_request
def get_transactions():
    try:
        # Gets the phone number from the jwt
        # and finds the user with the query
        full_phone_number = get_jwt_identity()
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
