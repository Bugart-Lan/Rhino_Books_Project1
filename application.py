import os

from flask import Flask, session, render_template, redirect, request, jsonify, url_for
from flask_session import Session
from flask_dotenv import DotEnv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from goodreads import *

app = Flask(__name__)
env = DotEnv(app)
env.init_app(app)
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
    return render_template("registration.html", wrong = False)

@app.route("/create", methods=["POST"])
def create():
    """Create a new acccount."""
    #Get form information.
    username = request.form.get("username")
    password = request.form.get("password")
    tmp = Account.query.filter_by(username=username).first()
    if tmp:
        return render_template("registration.html", wrong = True)
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
    if way and way != "year" and keyword:
        books = Books.query.filter(getattr(Books, way).like(f"%{keyword}%")).order_by(Books.id).all()
    elif way == "year" and isInt(keyword):
        books = Books.query.filter_by(year = keyword)
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
    reviews = db.execute(f"SELECT rating, comment, username, review.id FROM review\
                        JOIN accounts ON review.user_id = accounts.id\
                        WHERE review.book_id = {id};").fetchall()
    count = len(reviews)
    rate = True
    for review in reviews:
        if session['username'] == review.username:
            rate = False
            break
    book = Books.query.filter_by(id=id).first()
    ratings = get_ratings(book.isbn)
    return render_template("book_page.html", book = book, rate = rate, reviews = reviews, count = count, ratings = ratings, user = session['username'])

@app.route("/add_comment/<book_id>", methods=["POST"])
def add_comment(book_id):
    comment = request.form.get("comment")
    comment = comment.replace('\n', '<br>')
    rating = request.form.get("rating")
    review = Review(rating = rating, comment = comment, user_id = session['id'], book_id = book_id)
    review.add()
    return redirect(f"/book_page/{book_id}")

@app.route("/edit_page/<review_id>")
def edit_page(review_id):
    my_review = Review.query.filter_by(id=review_id).first()
    reviews = db.execute(f"SELECT rating, comment, username FROM review\
                        JOIN accounts ON review.user_id = accounts.id\
                        WHERE review.book_id = {my_review.book_id};").fetchall()
    book = Books.query.filter_by(id=my_review.book_id).first()
    print(my_review.comment)
    return render_template("edit.html", book = book, reviews = reviews, count = len(reviews), ratings = get_ratings(book.isbn), user = session['username'], my_review = my_review)

@app.route("/edit/<review_id>", methods=["POST"])
def edit(review_id):
    new_comment = request.form.get("new_comment")
    new_comment = new_comment.replace('\n', '<br>')
    new_rating = request.form.get("new_rating")
    review = Review.query.get(review_id)
    review.edit_comment(new_comment, new_rating)
    return redirect(f"/book_page/{review.book_id}")

@app.route("/modify_account")
def modify_account():
    return render_template("modify.html", wrong = False)

@app.route("/change_password", methods=["POST"])
def change_password():
    username = request.form.get("username")
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    account = Account.query.filter_by(username=username, password=old_password).first()
    if not account:
        return render_template("modify.html", wrong = True)
    account.update_password(new_password)
    return logout()

@app.route("/api/<isbn>")
def api(isbn):
    book = Books.query.filter_by(isbn=isbn).first()
    ratings = get_ratings(isbn)
    return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": isbn,
    "review_count": ratings['ratings_cnt'],
    "average_score": ratings['av_rating']
    })
