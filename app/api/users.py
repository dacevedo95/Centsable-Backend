from flask import jsonify, request, url_for, g, abort, current_app
from app.api import bp
from app.models import User
from app.api.auth import verify_request
from app.api.errors import error_response

@bp.route('/user/exists', methods=['POST'])
@verify_request
def check_user_exists():
    pass
