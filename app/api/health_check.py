from flask import jsonify, request
from app.api import bp
from app.api.errors import error_response


@bp.route('/', methods=['GET'])
def health_check():
    return error_response(200)
