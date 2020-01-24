from functools import wraps

from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, verify_jwt_refresh_token_in_request

def verify_request(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)

    return wrapper

def verify_refresh_request(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_refresh_token_in_request()
        return fn(*args, **kwargs)

    return wrapper
