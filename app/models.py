import base64
from datetime import datetime, timedelta
import os

from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    phone_number = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User: {0}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'phoneNumber': self.phone_number
        }
        return data

    def from_dict(self, data, new_user=False):
        self.first_name = data['firstName']
        self.last_name = data['lastName']
        self.phone_number = data['phoneNumber']

        if new_user and 'password' in data:
            self.set_password(password=data['password'])
