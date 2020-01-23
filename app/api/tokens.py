from flask import jsonify, g
from app import db
from app.api import bp
from app.api.auth import basic_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """
    This endpoint is used for users to get bearer tokens

    This request receives a email and password for login purposes, and uses the auth.verify_password function in the
    'auth' module. If the return is True (email and password are correct), we then call the get token method to retrieve
    the existing token, or generate a new one if it is expiring or expired
    """
    
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})
