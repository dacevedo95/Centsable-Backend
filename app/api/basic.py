from flask import jsonify, request, url_for, g, abort, current_app
from app.api import bp
from app.models import User
from app.api.auth import token_auth
from app.api.errors import error_response

@bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({
        'message': 'Hello, World!'
    })

@bp.route('/secret', methods=['GET'])
@token_auth.login_required
def secret():
    return jsonify({
        'secret': 42
    })
