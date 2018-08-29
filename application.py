import os

from flask import Flask, session, render_template, redirect, request, jsonify, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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
    if 'username' in session:
        session.pop('user_message', None)
        return redirect(url_for('user'))
    return render_template("login.html", wrong = False)

@app.route("/login_fail")
def login_fail():
    """Login failure."""
    #Page with alert message.
    return render_template("login.html", wrong = True)

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
        return redirect("/login_fail")
    session['id'] = account.id
    session['username'] = username
    return redirect(url_for('user'))

@app.route("/user")
def user():
    if 'username' not in session:
        return redirect("/")
    found = True
    if 'user_message' in session and session['user_message'] == 'notFound':
        found = False
    return render_template("search.html", found = found, username = session['username'])

@app.route("/search")
def search():
    way = request.args.get("ways")
    keyword = request.args.get("keyword")
    if way != "Choose..." and keyword:
        books = Books.query.filter(getattr(Books, way).like(f"%{keyword}%")).order_by(Books.id).all()
    else:
        books = False
    if not books:
        session['user_message'] = 'notFound'
        return redirect(f"/user")
    session.pop('user_message', None)
    return render_template("results.html", books = books)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")

@app.route("/book_page/<id>")
def book_page(id):
    reviews = db.execute(f"SELECT rating, comment, username FROM review\
                        JOIN accounts ON review.user_id = accounts.id\
                        WHERE review.book_id = {id};").fetchall()
    count = len(reviews)
    rate = True
    for review in reviews:
        if session['username'] == review.username:
            rate = False
            break
    book = Books.query.filter_by(id=id).first()
    return render_template("book_page.html", book = book, rate = rate, reviews = reviews, count = count)

@app.route("/add_comment/<book_id>", methods=["POST"])
def add_comment(book_id):
    return
