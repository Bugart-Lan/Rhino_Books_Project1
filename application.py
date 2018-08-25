import os

from flask import Flask, session, render_template, redirect, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("login.html", wrong = False)

@app.route("/register")
def register():
    return render_template("registration.html")

@app.route("/create", methods=["POST"])
def create():
    """Create a new acccount."""
    #Get form information.
    username = request.form.get("username")
    password = request.form.get("password")
    account = Account(username = username, password = password)
    account.add()
    return redirect("/")

@app.route("/verify", methods=["POST"])
def verify():
    username = request.form.get("username")
    password = request.form.get("password")
    account = Account.query.filter_by(username=username, password=password).first()
    if not account:
        return render_template("login.html", wrong = True)
    return render_template("search.html")

@app.route("/search")
def search():
    way = request.form.get("ways")
    key = request.form.get("key")
    way = 'title'
    #problem
    books = Book.query.filter(getattr(Book, way).like(f"%{key}%")).all()
    find = True
    if not book:
        find = False
    return render_template("results.html", find = find, books = books)
