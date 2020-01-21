from flask import jsonify, request, url_for, g, abort
from app.api import bp

@bp.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Hello, World!'
    })
