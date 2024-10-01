from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import inspect

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    phone_number = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    state = db.Column(db.String(50))
    travel_style = db.Column(db.String(50))
    preferences = relationship("Preference", back_populates="user")

class TravelDestination(db.Model):
    __tablename__ = 'travel_destinations'
    destination_id = db.Column(db.Integer, primary_key=True)
    destination_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    style = db.Column(db.String(50))
    tags = db.Column(db.String(255))
    preferences = relationship("Preference", back_populates="destination")

class Preference(db.Model):
    __tablename__ = 'preferences'
    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.phone_number'))
    destination_id = db.Column(db.Integer, db.ForeignKey('travel_destinations.destination_id'))
    style = db.Column(db.String(50))
    tags = db.Column(db.String(255))
    user = relationship("User", back_populates="preferences")
    destination = relationship("TravelDestination", back_populates="preferences")

def init_db(app):
    db.init_app(app)
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # List of all our models
        models = [User, TravelDestination, Preference]
        
        for model in models:
            if model.__tablename__ not in existing_tables:
                try:
                    model.__table__.create(db.engine)
                    print(f"Created table: {model.__tablename__}")
                except Exception as e:
                    print(f"Error creating table {model.__tablename__}: {e}")
            else:
                print(f"Table {model.__tablename__} already exists")

# You can add other database-related functions here, such as:
# - Functions to add sample data
# - Functions to query or update data
# - Any other database utility functions