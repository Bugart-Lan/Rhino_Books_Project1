import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    cnt = 0

    for isbn, title, author, year in reader:
        cnt += 1
        db.execute("INSERT INTO books (id, isbn, title, author, year) VALUES (:id, :isbn, :title, :author, :year)",
                    {"id": cnt, "isbn": isbn, "title": title, "author": author, "year": int(year)})

    db.commit()

if __name__ == "__main__":
    main()
