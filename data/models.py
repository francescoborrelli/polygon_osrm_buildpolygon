#  Copyright (c) 2020. AV Connect Inc.
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declarative_base
from . import db
import datetime
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Float, BigInteger, Boolean

Base = declarative_base()


class WSDataModel(object):
    def to_dict(self):
        types = (int, float, str, datetime.datetime, BigInteger)
        me = self.__dict__
        return { key:me[key] for key in me if not me[key] or type(me[key]) in types}


class Driver(db.Model, Base, WSDataModel):
    """
    Individual test drivers.  This is not an auth table!
    """
    __tablename__ = 'driver'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))


class Vehicle(db.Model, Base, WSDataModel):
    """
    Vehicles
    """
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    #current_ip = db.Column(db.String(30), nullable=True)



class Drive(db.Model, Base, WSDataModel):
    """
    Drives undertaken by driver.
    """
    __tablename__ = 'drive'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    driver = db.relationship(Driver)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    vehicle = db.relationship(Vehicle)


class User(db.Model, Base, UserMixin):
    """User account model."""

    __tablename__ = 'flasklogin-users'
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(100),
                     nullable=False,
                     unique=False)
    email = db.Column(db.String(40),
                      unique=True,
                      nullable=False)
    password = db.Column(db.String(200),
                         primary_key=False,
                         unique=False,
                         nullable=False)
    website = db.Column(db.String(60),
                        index=False,
                        unique=False,
                        nullable=True)
    created_on = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)
    last_login = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)
