from app import db, login
from enum import Enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    requests = db.relationship('Request', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(Enum):
    CLIENT_A = 'Client A'
    CLIENT_B = 'Client B'
    CLIENT_C = 'Client C'

    @classmethod
    def choices(cls):
        return [(choice, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(item) if not isinstance(item, cls) else item

    def __str__(self):
        return self.value

class Area(Enum):
    POLICIES = 'Policies'
    BILLING = 'Billing'
    CLAIMS = 'Claims'
    REPORTS = 'Reports'

    @classmethod
    def choices(cls):
        return [(choice, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(item) if not isinstance(item, cls) else item

    def __str__(self):
        return self.value

class Request(db.Model):
    id = db.Column(db.Integer, db.Sequence('id', start=0, increment=1), index=True)
    title = db.Column(db.String(140), index=True)
    description = db.Column(db.String(4096))
    client = db.Column(db.Enum(Client), primary_key=True)
    priority = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    target_date = db.Column(db.DateTime, index=True)
    product_area = db.Column(db.Enum(Area), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
