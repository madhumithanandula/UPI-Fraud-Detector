# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm  import relationship
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50))
    payment_gateway = db.Column(db.String(50))
    state = db.Column(db.String(50))
    merchant_category = db.Column(db.String(50))
    prediction = db.Column(db.String(20))
    confidence = db.Column(db.Float)
    # Link to User (One-to-Many Relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', backref='transactions')  # This allows you to access user's transactions
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    complaint_details = db.Column(db.Text, nullable=False)
    transaction_details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # link to User
    user = relationship('User', backref='complaints')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
