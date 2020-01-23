from flask import jsonify, request, url_for, g, abort, current_app
from app.api import bp
from app.models import User
from app.api.auth import token_auth
from app.api.errors import error_response

@bp.route('/', methods=['GET'])
@token_auth.login_required
def index():
    return jsonify({
        'message': 'Hello, World!'
    })
