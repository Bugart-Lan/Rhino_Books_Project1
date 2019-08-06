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
    def update_password(self, new_password):
        self.password = new_password
        db.session.commit()

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    isbn = db.Column(db.String, nullable = False)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.Integer, nullable = False)

class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key = True)
    rating = db.Column(db.Integer, nullable = False)
    comment = db.Column(db.Text, nullable = True)
    user_id = db.Column(db.Integer, nullable = False)
    book_id = db.Column(db.Integer, nullable = False)
    def add(self):
        db.session.add(self)
        db.session.commit()
    def edit_comment(self, new_comment):
        self.comment = new_comment
        db.session.commit()
