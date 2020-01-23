from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    """
    This function is called whenever the @basic_auth.login_required decorator is called (Just for api/v1/token)

    If first looks up a user by their email, and returns False if their is no user with that email.
    If a user is found, we than check the password passed. If the password is correct, we return True. Else, we
    return false.
    """

    # Tries to find a user by the given email
    user = User.query.filter_by(email=email).first()
    # Returns false if the user does not exist
    if user is None:
        return False
    # Sets the user as a global variable
    g.current_user = user
    # Checks the password of the user
    return user.check_password(password)

@basic_auth.error_handler
def basic_auth_error():
    """
    This function is triggered whenever the above "verify_password" function returns False.

    We return a 401 "Unauthorized" message stating "We don't know who you're trying to be"
    """

    return error_response(401)

@token_auth.verify_token
def verify_token(token):
    """
    This function is called whenever the @token_auth.login_required decorator is called
    """
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    return error_response(401)
