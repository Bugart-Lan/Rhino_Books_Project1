import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    def add(self):
            db.session.add(self)
            db.session.commit()

class Book(db.Model):
    __tablename = "books"
    id = db.Column(db.Integer, primary_key = True)
    isbn = db.Column(db.String, nullable = False)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.Integer, nullable = False)
