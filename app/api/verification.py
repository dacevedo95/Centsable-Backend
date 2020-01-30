from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.api import bp
from app.api.errors import error_response

import json
import requests


@bp.route('/send-verification', methods=['POST'])
def send_verification():
    pass


@bp.route('/check-verification', methods=['POST'])
def check_verification():
    pass
