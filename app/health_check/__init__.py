from flask import Blueprint

bp = Blueprint('health_check', __name__)

from app.health_check import health_check
