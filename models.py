import os

from flask import Flask
from flask_sqlalchemy import flask_sqlalchemy

db = SQLAlchemy()

class account(db.model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
