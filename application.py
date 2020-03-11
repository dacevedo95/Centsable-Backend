from app import create_app, db
from app.models import User
from flask import request

application = create_app()

@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

@application.before_request
def log_request():
    application.logger.info('{0} {1} \n{2}{3}'.format(request.method, request.path, request.headers, request.data))
