import base64
from datetime import datetime, timedelta
import os
import datetime

from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    country_calling_code = db.Column(db.String(8))
    phone_number = db.Column(db.String(32), index=True, unique=True)
    full_phone_number = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    verified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    transactions = db.relationship('Transaction', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User: {0}>'.format(self.phone_number)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'countryCallingCode': self.country_calling_code,
            'phoneNumber': self.phone_number,
            'createdAt': self.created_at
        }
        return data

    def from_dict(self, data, new_user=False):
        self.first_name = data['firstName']
        self.last_name = data['lastName']
        self.country_calling_code = data['countryCode']
        self.phone_number = data['phoneNumber']
        self.full_phone_number = '+' + data['countryCode'] + data['phoneNumber']

        if new_user and 'password' in data:
            self.set_password(password=data['password'])

    def reset_password(self, newPassword):
        self.set_password(password=newPassword)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(128))
    category = db.Column(db.String(32))
    price = db.Column(db.Float())
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_recurring = db.Column(db.Boolean)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'createdAt': self.created_at
        }
        return data

    def from_dict(self, data, author):
        self.name = data['name']
        self.category = data['category']
        self.price = data['price']
        self.created_at = datetime.datetime.strptime(data['createdAt'], '%Y-%m-%d')
        self.is_recurring = data['isRecurring']
        self.author = author
