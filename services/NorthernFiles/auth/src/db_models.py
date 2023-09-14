from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql.base import MSText
from Crypto.PublicKey import RSA
import uuid
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    username = db.Column(MSText, unique=True, nullable=False)
    name = db.Column(MSText, nullable=False)
    capsule = db.Column(db.LargeBinary, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'capsule': self.capsule
        }
    
    @property
    def serialize_no_key(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
        }


class LoginServerStorage(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    ss = db.Column(db.LargeBinary, nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)