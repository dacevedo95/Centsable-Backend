from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

import logging
from logging.handlers import RotatingFileHandler

import os


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config=Config):

    # Creates a flask app and attaches a configuration to it
    app = Flask(__name__)
    app.config.from_object(config)

    # attach the instances to the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Registers the API blueprint to the app instance
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    # Registers the API blueprint to the app instance
    from app.errors import bp as error_handler_bp
    app.register_blueprint(error_handler_bp)

    # Only sets up the logger in production, when debugging and testing are off
    if not app.debug and not app.testing:
        # Checks if we set up a mail server
        # If so, we create a logger that sends emails whenver there is an error
        if app.config['MAIL_SERVER']:
            # Initializes our authentication
            # If a username and password exist in our environment, we use that for our authentication
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            # Initializes our security
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            # Sets up our mail handler from our environment variables
            # We then set it's threshold to log only ERROR and FATAL
            # Lastly, we add out mil handler to our application's logger
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Clout Game Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        # Checks if we wish to log to the console
        # If we do not, then we will set up a rotating file handler
        if app.config['LOG_TO_STDOUT']:
            # Sets up the console logger
            # Sets the logger threshold at INFO
            # Lastly, it adds the handler to our app's logger
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            # Checks if the 'logs' directory exists
            # If it doesn't, we create the 'logs' directory
            if not os.path.exists('logs'):
                os.mkdir('logs')
            # Creates the rotating file handler
            # Sets the format of how we wish to log a message
            # Sets the threshold of the logger to INFO and above
            # Adds the handler to the app's logger
            file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        # Sets the threshold for the app's overall logger
        # Sends a message to log as an initiator
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    # Returns the app instance
    return app

from app import models
