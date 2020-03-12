from flask import jsonify, request
from app.health_check import bp


@bp.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'message': 'success'
    })
